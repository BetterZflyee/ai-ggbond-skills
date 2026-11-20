import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
fake=types.ModuleType('config_loader');fake.load_all_env=lambda:{};fake.apply_env_to_os=lambda:None;fake.get_config_status=lambda:{}
with mock.patch.dict(sys.modules,{'config_loader':fake}):
    spec=importlib.util.spec_from_file_location('sticker_legacy_test',ROOT/'scripts/generate_sticker_images_v2.py')
    legacy=importlib.util.module_from_spec(spec);sys.modules[spec.name]=legacy;spec.loader.exec_module(legacy)
spec=importlib.util.spec_from_file_location('sticker_manager_test',ROOT/'scripts/sticker_manager.py')
manager=importlib.util.module_from_spec(spec);spec.loader.exec_module(manager)


class LegacyTests(unittest.TestCase):
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='sticker-legacy-test-'))
        self.network=mock.patch.object(legacy.requests,'post',side_effect=AssertionError('No live API calls in tests'))
        self.network.start()

    def tearDown(self):
        self.network.stop();shutil.rmtree(self.temp)

    def test_paragraphs_and_long_details_reach_prompt_without_tags(self):
        detail='这一段必须保留。'*20
        result=legacy.ContentAnalyzer.extract_content('# 标题\n\n普通段落有 12.00%。\n\n## 章节\n正文不是列表。\n- '+detail+'\n\n#公众号 #测试')
        self.assertIn('普通段落有 12.00%。',result['core_message'])
        self.assertIn(detail,result['core_message'])
        self.assertIn('正文不是列表。',result['sections'][0]['points'])
        self.assertEqual(result['hashtags'],['公众号','测试'])
        self.assertNotIn('#公众号',result['core_message'])

    def test_single_configured_endpoint_never_adds_a_provider(self):
        with mock.patch.dict(os.environ,{'YUNWU_BASE_URL':'https://example.test/v1','YUNWU_BASE_URLS':''}):
            g=legacy.StickerImageGenerator(api_key='unit-test-key')
        self.assertEqual(g.base_urls,['https://example.test'])

    def test_ratio_request_is_mathematically_correct(self):
        g=legacy.StickerImageGenerator(api_key='unit-test-key',base_urls=['https://example.test'])
        with mock.patch.dict(os.environ,{'YUNWU_IMAGE_SIZE_16_9':'1600x900'}),mock.patch.object(g,'generate',return_value='mock') as call:
            g.generate_sticker_image('题目','准确内容',legacy.STICKER_STYLES['tech'],ratio='16:9')
        a,b=map(int,call.call_args.kwargs['size'].split('x'))
        self.assertEqual(a/b,16/9)

    def test_auth_rejection_stops_without_provider_switch_or_retry(self):
        g=legacy.StickerImageGenerator(api_key='unit-test-key',base_urls=['https://example.test','https://fallback.test'])
        response=mock.Mock(status_code=401)
        with mock.patch.object(legacy.requests,'post',return_value=response) as post:
            with self.assertRaises(legacy.ImageRequestRejected):g.generate('测试',max_retries=3)
        self.assertEqual(post.call_count,1)

    def test_partial_generation_fails_and_keeps_completed_output(self):
        file=self.temp/'draft.md';file.write_text('# 标题\n## 甲\n第一段\n## 乙\n第二段')
        generator=mock.Mock();generator.generate_sticker_image.side_effect=['done',RuntimeError('mock failure')]
        generator.save_image.side_effect=lambda result,file,*args:Path(file).write_bytes(b'completed-image-test')
        with mock.patch.object(legacy,'StickerImageGenerator',return_value=generator):
            with self.assertRaisesRegex(RuntimeError,'1/2'):
                legacy.generate_sticker_images_from_markdown(str(file),output_dir=str(self.temp/'images'),image_interval=0)
        self.assertEqual(len(list((self.temp/'images').glob('*.png'))),1)
        self.assertEqual(generator.generate_sticker_image.call_args.kwargs['style'].name, 'editorial-magazine')
        self.assertEqual(generator.generate_sticker_image.call_args.kwargs['model'], 'gpt-image-2.6-flare')

    def test_repeated_manager_save_does_not_overwrite_existing_draft(self):
        m=manager.StickerManager(str(self.temp))
        a=m.generate_sticker('中文标题','原稿');b=m.generate_sticker('中文标题','修订')
        self.assertNotEqual(a['folder'],b['folder']);self.assertIn('原稿',a['content'].read_text())
        self.assertIn('中文标题',a['folder'].name)


if __name__=='__main__':unittest.main()
