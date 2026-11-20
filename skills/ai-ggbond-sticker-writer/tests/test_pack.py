import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sticker_pack',ROOT/'scripts/sticker_pack.py')
pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
IMAGE=ROOT.parent/'ai-ggbond-wechat-layout/assets/demo/layout-example.png'


class PackTests(unittest.TestCase):
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='sticker-pack-test-'))
        self.source=self.temp/'plan.json';self.out=self.temp/'delivery'
        self.data={'schema_version':1,'scene':'newspic','meta':{'title':'贴图测试'},'caption':'数字保留 12.00%，链接保持 https://example.com/a_(b)。','tags':['公众号','图文','核对'],'expected_image_count':1,'sources':[{'id':'local','title':'本地演示'}],'images':[{'id':'cover','role':'cover','heading':'保留内容','text':['段落、引用和数据'],'ratio':'36:35','asset':str(IMAGE),'source_min_text_px':32,'source_ids':['local'],'review':{'status':'passed','method':'visual','sha256':hashlib.sha256(IMAGE.read_bytes()).hexdigest()}}]}

    def tearDown(self):
        shutil.rmtree(self.temp)

    def build(self):
        self.source.write_text(json.dumps(self.data,ensure_ascii=False))
        return pack.build(self.source,self.out)

    def read(self,name):
        return json.loads((self.out/name).read_text())

    def test_native_text_asset_and_order_are_preserved(self):
        self.build();bundle=self.read('newspic-bundle.json')
        self.assertEqual(bundle['content'],self.data['caption']+'\n\n#公众号 #图文 #核对')
        self.assertEqual((self.out/'caption.txt').read_text(),bundle['content'])
        self.assertEqual((self.out/bundle['images'][0]['path']).read_bytes(),IMAGE.read_bytes())
        self.assertEqual(bundle['status'],'ready')
        self.assertEqual(pack.audit(self.out)['status'],'passed')

    def test_native_markup_is_rejected_instead_of_uploaded(self):
        self.data['caption']='## 标题\n**强调**'
        with self.assertRaises(ValueError):self.build()
        self.assertFalse(self.out.exists())

    def test_tags_never_enter_image_prompt(self):
        self.data['images'][0]['text'].append('#公众号')
        with self.assertRaises(ValueError):self.build()

    def test_custom_prompt_is_preserved_and_hex_color_allowed(self):
        prompt='沿用 #0A1628 深蓝色，标题「保留内容」，配科技插画。'
        self.data['images'][0]['prompt']=prompt
        self.build();self.assertEqual((self.out/'prompts/01-cover.md').read_text(),prompt+'\n')

    def test_missing_image_never_becomes_ready(self):
        del self.data['images'][0]['asset'];self.build()
        self.assertEqual(self.read('newspic-bundle.json')['status'],'review_required')
        self.assertIn('MISSING_IMAGE',[f['code'] for f in self.read('design-review.json')['findings']])

    def test_wrong_aspect_and_small_text_are_reported(self):
        self.data['images'][0].update(ratio='16:9',source_min_text_px=12)
        self.build();codes=[x['code'] for x in self.read('design-review.json')['findings']]
        self.assertIn('ASPECT_MISMATCH',codes);self.assertIn('IMAGE_TEXT_SMALL',codes)

    def test_review_hash_does_not_survive_image_change(self):
        self.data['images'][0]['review']['sha256']='0'*64
        self.build();self.assertEqual(self.read('newspic-bundle.json')['status'],'review_required')

    def test_caption_budget_reports_but_does_not_truncate(self):
        self.data['caption']='图😀'*260
        self.build();r=self.read('design-review.json')
        self.assertIn('CAPTION_BUDGET',[f['code'] for f in r['findings']])
        self.assertTrue((self.out/'caption.txt').read_text().startswith(self.data['caption']))
        self.assertGreater(r['caption']['body_utf16_units'],r['caption']['body_codepoints'])

    def test_image_count_and_source_links_must_match(self):
        for edit in ['count','source']:
            plan=copy.deepcopy(self.data)
            if edit=='count':plan['expected_image_count']=2
            else:plan['images'][0]['source_ids']=['missing']
            with self.assertRaises(ValueError):pack.validate(plan)

    def test_article_reuse_keeps_structured_content_and_excludes_cover(self):
        second=copy.deepcopy(self.data['images'][0]);second.update(id='detail',role='steps')
        self.data['images'].append(second);self.data['expected_image_count']=2
        blocks=[{'type':'paragraph','text':'原文的 12.00% 与 2 个空格  均保留。'},{'type':'steps','items':[{'title':'读取','text':'先读原稿'}]},{'type':'image','image_id':'detail'}]
        self.data['article_reuse']={'meta':{'title':'长文'},'cover_image_id':'cover','blocks':blocks}
        self.build();article=self.read('layout-input.json')
        self.assertEqual(article['blocks'][:2],blocks[:2]);self.assertTrue(article['meta']['cover'].endswith('01-cover.png'))
        self.assertTrue(article['blocks'][2]['src'].endswith('02-detail.png'))

    def test_cover_is_not_implicitly_duplicated_in_article(self):
        self.data['article_reuse']={'cover_image_id':'cover','blocks':[{'type':'image','image_id':'cover'}]}
        with self.assertRaises(ValueError):self.build()
        self.assertFalse(self.out.exists())

    def test_no_silent_overwrite_and_tampering_detected(self):
        self.build()
        with self.assertRaises(ValueError):self.build()
        (self.out/'caption.txt').write_text('changed')
        self.assertEqual(pack.audit(self.out)['changed_or_missing'],['caption.txt'])


if __name__=='__main__':unittest.main()
