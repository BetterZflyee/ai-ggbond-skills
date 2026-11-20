import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('install_local',ROOT/'scripts/install_local.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='wechat-install-test-'))
        self.user_root=self.temp/'user';self.backup=self.temp/'backups'
        self.entry=self.user_root/'.hermes/skills/creative/ai-ggbond-article-writer/SKILL.md'
        self.entry.parent.mkdir(parents=True)
        self.original='---\nname: existing-writer\ndescription: existing\n---\n\n# Existing\n\n用户已有工作内容保持原样。\n'
        self.entry.write_text(self.original)

    def tearDown(self):
        shutil.rmtree(self.temp)

    def test_backup_preservation_and_repeat_install(self):
        plan=installer.install(self.user_root,self.backup)
        self.assertEqual(plan['status'],'plan')
        self.assertEqual(self.entry.read_text(),self.original)
        result=installer.install(self.user_root,self.backup,True)
        before=json.loads((Path(result['backup'])/'before.json').read_text())
        saved=next(x for x in before if x['kind']=='route')
        self.assertEqual(Path(saved['backup']).read_text(),self.original)
        self.assertIn('用户已有工作内容保持原样。',self.entry.read_text())
        for target in result['destinations']:
            self.assertEqual(installer.package_hashes(Path(target)),result['package_hashes'])
        repeated=installer.install(self.user_root,self.backup,True)
        self.assertFalse(repeated['routes'][0]['changed'])
        self.assertEqual(self.entry.read_text().count(installer.START),1)

    def test_unrelated_target_not_overwritten(self):
        target=self.user_root/'.codex/skills'/installer.NAME
        target.mkdir(parents=True)
        (target/'SKILL.md').write_text('---\nname: unrelated\n---\nOriginal')
        with self.assertRaises(ValueError):
            installer.install(self.user_root,self.backup,True)
        self.assertIn('Original',(target/'SKILL.md').read_text())
        self.assertEqual(self.entry.read_text(),self.original)


if __name__=='__main__':
    unittest.main()
