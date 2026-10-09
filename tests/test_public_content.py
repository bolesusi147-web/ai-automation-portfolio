import tempfile
import unittest
from pathlib import Path
from tools.check_public_content import findings, scan_paths


class PublicContentTests(unittest.TestCase):
    def test_tokens_are_reported_by_category_without_exposing_values(self):
        for secret in ['sk-'+'A'*35, 'gh'+'p_'+'b'*36, '-----BEGIN '+'OPENSSH PRIVATE KEY-----']:
            result=findings('fixture.txt',secret)
            self.assertTrue(result)
            self.assertNotIn(secret,str(result))

    def test_nonpublic_addresses_and_unexpected_email_are_flagged(self):
        for value in ['192.'+'168.1.1','person'+'@private.example','https'+'://'+'internal'+'.example/api']:
            self.assertTrue(findings('fixture.txt',value))
        self.assertEqual(findings('README.md','Contact bolesusi147@gmail.com; https://github.com/bolesusi147-web/Projects'),[])

    def test_hidden_config_and_binary_files_are_never_silently_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'.env').write_text('anything');(root/'recording.wav').write_bytes(b'\x00\x01')
            results=scan_paths(root,['.env','recording.wav'])
            self.assertEqual({r['category'] for r in results},{'forbidden_file','binary_or_media'})

    def test_scanner_rejects_symlinks_and_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'real.txt').write_text('safe');(root/'link.txt').symlink_to(root/'real.txt')
            results=scan_paths(root,['link.txt','missing.txt'])
            self.assertEqual({r['category'] for r in results},{'symlink','unreadable_file'})
