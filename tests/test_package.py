import json
import pathlib
import shutil
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from validate import ROOT, FILES, validate
from package import build

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        for name in FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
    def tearDown(self):
        self.tmp.cleanup()
    def alter(self, name, fn):
        p = self.root / name
        value = json.loads(p.read_text()); fn(value)
        p.write_text(json.dumps(value))
    def test_valid(self):
        self.assertEqual(validate(self.root), len(FILES))
    def test_unknown_core_field(self):
        self.alter('plugin.json', lambda p: p.update(mcpServers={}))
        with self.assertRaises(Exception): validate(self.root)
    def test_wrong_transport(self):
        self.alter('mcp.json', lambda p: p['mcpServers']['billr'].update(type='http'))
        with self.assertRaises(Exception): validate(self.root)
    def test_wrong_endpoint(self):
        self.alter('mcp.json', lambda p: p['mcpServers']['billr'].update(url='http://localhost:3000'))
        with self.assertRaises(ValueError): validate(self.root)
    def test_credentials(self):
        self.alter('config/cursor.mcp.json', lambda p: p['mcpServers']['billr'].update(headers={'Authorization':'Bearer placeholder'}))
        with self.assertRaises(ValueError): validate(self.root)
    def test_path_escape(self):
        self.alter('.cursor-plugin/plugin.json', lambda p: p.update(logo='../outside.png'))
        with self.assertRaises(ValueError): validate(self.root)
    def test_missing_asset(self):
        (self.root/'assets/icon.png').unlink()
        with self.assertRaises(ValueError): validate(self.root)
    def test_symlink(self):
        p=self.root/'assets/icon.png'; p.unlink(); p.symlink_to(ROOT/'assets/icon.png')
        with self.assertRaises(ValueError): validate(self.root)
    def test_metadata_drift(self):
        self.alter('.claude-plugin/plugin.json', lambda p: p.update(version='0.0.0'))
        with self.assertRaises(ValueError): validate(self.root)
    def test_secret(self):
        (self.root/'NOTICE').write_text('sk_live_' + 'x'*24)
        with self.assertRaises(ValueError): validate(self.root)
    def test_archive_excludes_unlisted(self):
        (self.root/'.env').write_text('PRIVATE=not-for-release')
        target=build(self.root)
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(sorted(archive.namelist()), sorted(FILES))
    def test_archive_reproducible(self):
        first=build(self.root).read_bytes()
        self.assertEqual(first, build(self.root).read_bytes())

if __name__=='__main__': unittest.main()
