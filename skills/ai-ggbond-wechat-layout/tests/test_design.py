import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('layout_v2',ROOT/'scripts/layout.py')
layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='wechat-design-test-'))
        self.input=self.temp/'input.json';self.out=self.temp/'bundle'

    def tearDown(self):
        shutil.rmtree(self.temp)

    def build(self,blocks,profile='felix-clean'):
        self.input.write_text(json.dumps({'schema_version':1,'meta':{'title':'排版测试'},'blocks':blocks},ensure_ascii=False))
        return layout.compile_bundle(self.input,self.out,profile)

    def test_compact_four_columns_keep_comparison(self):
        self.build([{'type':'table','headers':['项目','甲','乙','丙'],'rows':[['成本','12','18','23'],['用时','2','3','4']]}])
        body=(self.out/'body.html').read_text()
        report=json.loads((self.out/'design-review.json').read_text())
        self.assertEqual(report['tables'][0]['layout'],'table')
        self.assertEqual(body.count('<table '),1)
        self.assertEqual(report['tables'][0]['align'],['left','right','right','right'])

    def test_wide_comparison_repeats_key_without_losing_data(self):
        headers=['方案','需求理解','执行范围','验收条件','适用边界']
        rows=[['方案甲','先确认真实业务问题','按目标任务完整执行','读回最终生成结果','适用于稳定任务'],['方案乙','梳理变化后的场景','按新信息逐步执行','核对每一段变更','适用于探索任务']]
        self.build([{'type':'table','headers':headers,'rows':rows}])
        body=(self.out/'body.html').read_text();reader=layout.FieldReader();reader.feed(body)
        self.assertEqual(body.count('<table '),2)
        self.assertEqual(body.count('方案甲'),2)
        self.assertTrue(all(n==1 for n in reader.counts.values()))
        for row in rows:
            for cell in row:self.assertIn(cell,body)

    def test_poor_contrast_is_reported_without_rewriting(self):
        profile=layout.profile_load('felix-clean');profile['muted']='#BBBBBB'
        file=self.temp/'profile.json';file.write_text(json.dumps(profile))
        self.build([{'type':'paragraph','text':'保留这段话。'}],str(file))
        report=json.loads((self.out/'design-review.json').read_text())
        self.assertIn('LOW_CONTRAST',[x['code'] for x in report['findings']])
        self.assertIn('保留这段话。',(self.out/'body.html').read_text())

    def test_image_text_size_uses_real_dimensions(self):
        image=str(ROOT/'assets/demo/layout-example.png')
        self.build([{'type':'image','src':image,'role':'diagram','alt':'原图说明','source_min_text_px':12}])
        report=json.loads((self.out/'design-review.json').read_text())
        self.assertEqual(report['images'][0]['dimensions'],[720,700])
        self.assertAlmostEqual(report['images'][0]['estimated_min_text_px_at_320'],4.8)
        self.assertIn('IMAGE_TEXT_TOO_SMALL',[x['code'] for x in report['findings']])

    def test_code_whitespace_loss_fails_fidelity(self):
        original=layout.Renderer.field
        def changed(renderer,value,key,raw=False,copy=False):
            result=original(renderer,value,key,raw,copy)
            return result.replace('    return','return') if raw else result
        with mock.patch.object(layout.Renderer,'field',changed):
            with self.assertRaises(ValueError):
                self.build([{'type':'code','text':'def value():\n    return 42'}])
        self.assertFalse(self.out.exists())

    def test_url_with_parentheses_keeps_complete_destination(self):
        self.build([{'type':'paragraph','text':'参考[说明](https://example.com/a_(b))。'}])
        reader=layout.FieldReader();reader.feed((self.out/'body.html').read_text())
        self.assertEqual(reader.links,['https://example.com/a_(b)'])
        self.assertIn('参考说明。',layout.visible((self.out/'body.html').read_text()))

    def test_preview_scripts_do_not_enter_publish_html(self):
        self.build([{'type':'paragraph','text':'正文'}])
        self.assertNotIn('<script',(self.out/'article.html').read_text())
        self.assertIn('layout-preview-settings',(self.out/'reading-preview.html').read_text())
        self.assertEqual(layout.audit_bundle(self.out)['status'],'passed')

    def test_large_invalid_chart_value_returns_value_error(self):
        with self.assertRaises(ValueError):
            self.build([{'type':'chart','title':'图表','items':[{'label':'甲','value':10**1000},{'label':'乙','value':1}]}])


if __name__=='__main__':
    unittest.main()
