import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("layout",ROOT/"scripts/layout.py")
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix="wechat-layout-test-"))
        self.source = self.temp/"input.json"
        self.out = self.temp/"bundle"

    def tearDown(self):
        shutil.rmtree(self.temp)

    def build(self, blocks, meta=None, **kwargs):
        self.source.write_text(json.dumps({"schema_version":1,"meta":meta or {"title":"测试文章"},"blocks":blocks},ensure_ascii=False))
        return layout.compile_bundle(self.source,self.out,"felix-clean",**kwargs)

    def test_all_components_and_static_fallback(self):
        result=layout.compile_bundle(ROOT/"assets/demo/article.json",self.out,"felix-clean")
        data=json.loads((self.out/"article.json").read_text())
        self.assertEqual({b["type"] for b in data["blocks"]},layout.TYPES)
        self.assertGreater(result["fidelity_fields"],50)
        self.assertNotIn('<svg',(self.out/'article.html').read_text())
        self.assertIn('<svg',(self.out/'interactive.html').read_text())
        self.assertIn('完整信息',(self.out/'article.html').read_text())
        self.assertEqual(layout.audit_bundle(self.out)['status'],'passed')

    def test_markdown_metadata_lists_table_and_quotes(self):
        p=self.temp/'input.md'
        p.write_text('# 原标题\n\n**副标题：原摘要**\n\n第一段**重点**，数字12.00%。\n\n## 原章节\n\n> 原引用\n\n3. 第三项\n4. 第四项\n\n| 甲 | 乙 |\n|---|---|\n| a\\|b | 0.00 |\n\n```python\nx = "<tag>"\n```\n')
        result=layout.compile_bundle(p,self.out,'felix-clean')
        body=(self.out/'body.html').read_text()
        meta=json.loads((self.out/'handoff.json').read_text())['meta']
        self.assertEqual(meta['title'],'原标题')
        self.assertEqual(meta['summary'],'原摘要')
        self.assertNotIn('原标题',body)
        self.assertNotIn('原摘要',body)
        self.assertIn('start="3"',body)
        self.assertIn('a|b',body)
        self.assertIn('12.00%',body)
        self.assertEqual(result['validation']['phone_wechat'],'not_tested')

    def test_wide_table_keeps_every_cell(self):
        self.build([{'type':'table','layout':'records','headers':['一','二','三','四'],'rows':[['甲','12.00%','$0.00','丁'],['乙','0','-3','戊']]}])
        body=(self.out/'body.html').read_text()
        self.assertNotIn('<table',body)
        for value in ['甲','12.00%','$0.00','丁','乙','-3','戊']:
            self.assertIn(value,body)

    def test_invalid_table_does_not_create_bundle(self):
        with self.assertRaises(ValueError):
            self.build([{'type':'table','headers':['一','二'],'rows':[['少一列']]}])
        self.assertFalse(self.out.exists())

    def test_no_silent_overwrite_and_bad_rebuild_preserves_old(self):
        self.build([{'type':'paragraph','text':'旧稿保留'}])
        old=(self.out/'article.html').read_bytes()
        with self.assertRaises(ValueError):
            self.build([{'type':'paragraph','text':'新稿'}])
        with self.assertRaises(ValueError):
            self.build([{'type':'image','src':'missing.png'}],overwrite=True)
        self.assertEqual((self.out/'article.html').read_bytes(),old)
        self.build([{'type':'paragraph','text':'新稿'}],overwrite=True)
        self.assertIn('新稿',(self.out/'article.html').read_text())

    def test_assets_copy_and_missing_image_rejected(self):
        shutil.copy2(ROOT/'assets/demo/layout-example.png',self.temp/'space name.png')
        self.build([{'type':'image','src':'space name.png','alt':'图像'}])
        asset=json.loads((self.out/'handoff.json').read_text())['assets'][0]
        self.assertEqual((self.out/asset['src']).read_bytes(),(self.temp/'space name.png').read_bytes())
        self.assertEqual(asset['rights'],'not_checked')

    def test_cover_not_silently_repeated(self):
        image=str(ROOT/'assets/demo/layout-example.png')
        with self.assertRaises(ValueError):
            self.build([{'type':'image','src':image}],{'title':'标题','cover':image})

    def test_duplicate_ids_and_title_rejected(self):
        with self.assertRaises(ValueError):
            self.build([{'id':'same','type':'paragraph','text':'甲'},{'id':'same','type':'paragraph','text':'乙'}])
        with self.assertRaises(ValueError):
            self.build([{'type':'heading','text':'测试文章'}])

    def test_injection_is_escaped_or_rejected(self):
        self.build([{'type':'paragraph','text':'<script>alert(1)</script> & 中文'}])
        body=(self.out/'body.html').read_text()
        self.assertNotIn('<script>',body)
        self.assertIn('&lt;script&gt;',body)
        for value in ['[点我](javascript:alert)','[点我](data:text/html,hello)']:
            with self.assertRaises(ValueError):
                self.build([{'type':'paragraph','text':value}],overwrite=True)

    def test_chart_numeric_boundaries(self):
        for value in [True,float('nan'),float('inf'),-1]:
            with self.assertRaises(ValueError):
                self.build([{'type':'chart','title':'图','items':[{'label':'甲','value':value},{'label':'乙','value':2}]}])

    def test_unknown_structure_not_silently_dropped(self):
        for text in ['# 标题\n\n- 一级\n  - 二级','---\ntitle: >\n  复杂\n---\n正文','# 标题\n\n![图](x.png)后面还有正文','# 标题\n\n```\n未闭合']:
            with self.assertRaises(ValueError):
                layout.parse_markdown(text)

    def test_modified_bundle_detected(self):
        self.build([{'type':'paragraph','text':'原文'}])
        (self.out/'article.html').write_text('被替换')
        result=layout.audit_bundle(self.out)
        self.assertEqual(result['status'],'failed')
        self.assertIn('article.html',result['changed_or_missing'])

    def test_interactive_text_never_truncated(self):
        with self.assertRaises(ValueError):
            self.build([{'type':'reveal','prompt':'问题','answer':'非常长的答案'*100,'interactive':True}])
        self.assertFalse(self.out.exists())


if __name__=='__main__':
    unittest.main()
