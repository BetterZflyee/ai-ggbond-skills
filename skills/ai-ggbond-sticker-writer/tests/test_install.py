import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sticker_install', ROOT / 'scripts/install_local.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sticker-install-test-')
        self.home = Path(self.temp.name) / 'home'
        self.backups = Path(self.temp.name) / 'backups'
        self.layout = Path(self.temp.name) / 'layout'
        self.layout.mkdir()
        (self.layout / 'SKILL.md').write_text('---\nname: ai-ggbond-wechat-layout\n---\nLayout fixture\n')
        self.publisher = self.home / '.hermes/skills/productivity/ai-ggbond-post-to-wechat'
        (self.publisher / 'scripts').mkdir(parents=True)
        (self.publisher / 'scripts/wechat-api.ts').write_bytes(b'original publisher')
        (self.publisher / 'SKILL.md').write_text('---\nname: ai-ggbond-post-to-wechat\n---\nKeep this workflow.\n')
        self.old_route = (self.publisher / 'SKILL.md').read_bytes()
        self.patch = patch.object(module, 'patched_api', side_effect=lambda data: b'adapted publisher')
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def test_install_backs_up_reads_back_and_is_idempotent(self):
        before = module.install(self.home, self.layout, self.backups)
        self.assertEqual(before['status'], 'plan')
        self.assertFalse(self.backups.exists())
        self.assertEqual((self.publisher / 'SKILL.md').read_bytes(), self.old_route)
        result = module.install(self.home, self.layout, self.backups, apply=True)
        self.assertTrue(result['readback_passed'])
        self.assertEqual(len(result['packages']), 6)
        self.assertEqual((Path(result['backup']) / 'before.json').stat().st_mode & 0o777, 0o600)
        again = module.install(self.home, self.layout, self.backups)
        self.assertFalse(any(item['changed'] for item in again['packages'] + again['files']))
        self.assertEqual((self.publisher / 'SKILL.md').read_text().count(module.START), 1)

    def test_write_failure_restores_packages_and_existing_routes(self):
        real_write = module.atomic_write
        calls = 0
        def fail_once(path, data, mode=0o644):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated write failure')
            return real_write(path, data, mode)
        with patch.object(module, 'atomic_write', side_effect=fail_once):
            with self.assertRaisesRegex(OSError, 'simulated'):
                module.install(self.home, self.layout, self.backups, apply=True)
        self.assertEqual((self.publisher / 'SKILL.md').read_bytes(), self.old_route)
        self.assertEqual((self.publisher / 'scripts/wechat-api.ts').read_bytes(), b'original publisher')
        self.assertFalse((self.home / '.hermes/skills/creative/ai-ggbond-sticker-writer').exists())
        self.assertFalse((self.publisher / 'scripts/newspic-bundle.ts').exists())

    def test_route_preserves_other_modules_and_rejects_broken_markers(self):
        old = '---\nname: writer\n---\n<!-- BEGIN AI-GGBOND-WECHAT-LAYOUT -->keep<!-- END AI-GGBOND-WECHAT-LAYOUT -->\n原有写作规则'
        new = module.route(old, Path('/sticker'), Path('/layout'), 'writer')
        self.assertIn('<!-- BEGIN AI-GGBOND-WECHAT-LAYOUT -->keep<!-- END AI-GGBOND-WECHAT-LAYOUT -->', new)
        self.assertTrue(new.endswith('原有写作规则'))
        self.assertEqual(module.route(new, Path('/sticker'), Path('/layout'), 'writer'), new)
        with self.assertRaises(ValueError):
            module.route(old + module.START, Path('/sticker'), Path('/layout'), 'writer')

    def test_legacy_entry_is_preserved_and_unknown_revision_is_rejected(self):
        source_spec = json.loads((ROOT / 'adapters/legacy-hermes-entry.json').read_text())
        legacy = self.home / source_spec['path']
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes(b'user local changes')
        with self.assertRaisesRegex(ValueError, '旧合集'):
            module.install(self.home, self.layout, self.backups, apply=True)
        self.assertEqual(legacy.read_bytes(), b'user local changes')
        self.assertFalse(self.backups.exists())
        actual_sha = module.sha
        expected = source_spec['sha256']
        with patch.object(module, 'sha', side_effect=lambda data: expected if data == b'user local changes' else actual_sha(data)):
            result = module.install(self.home, self.layout, self.backups, apply=True)
        self.assertFalse(legacy.exists())
        retired = legacy.with_name(source_spec['retired_name'])
        self.assertEqual(retired.read_bytes(), b'user local changes')
        self.assertEqual(retired.stat().st_mode & 0o777, 0o600)
        self.assertTrue(result['readback_passed'])

    def test_current_repository_entry_can_remain_a_valid_install_source(self):
        source_spec = json.loads((ROOT / 'adapters/legacy-hermes-entry.json').read_text())
        entry = self.home / source_spec['path']
        entry.parent.mkdir(parents=True)
        entry.write_bytes((ROOT / 'SKILL.md').read_bytes())
        result = module.install(self.home, self.layout, self.backups, apply=True)
        self.assertTrue(result['readback_passed'])
        self.assertEqual(entry.read_bytes(), (ROOT / 'SKILL.md').read_bytes())
        self.assertFalse(any(f['kind'] == 'duplicate-entry' for f in result['files']))


if __name__ == '__main__':
    unittest.main()
