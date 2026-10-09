"""Publication boundaries for explicitly reviewed README graphics."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from tools.check_public_content import scan_paths


def png_pixel():
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(b'\x00\x00\x00\x00')) + chunk(b'IEND', b''))


class PublicVisualTests(unittest.TestCase):
    def prepare(self, root, content, path='assets/workflow.png', approve=True):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content)
        assets = ([dict(path=path, sha256=hashlib.sha256(content).hexdigest(),
                        bytes=len(content), media_type='image/png')] if approve else [])
        (root / 'assets').mkdir(exist_ok=True)
        (root / 'assets/manifest.json').write_text(json.dumps(dict(synthetic=True, assets=assets)))
        return path

    def test_reviewed_png_is_publishable_without_allowing_arbitrary_binaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.prepare(root, png_pixel())
            self.assertEqual(scan_paths(root, [path]), [])

    def test_changed_image_requires_new_review_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.prepare(root, png_pixel())
            (root / path).write_bytes(png_pixel() + b'changed')
            result = scan_paths(root, [path])
            self.assertEqual([x['category'] for x in result], ['visual_fingerprint_mismatch'])

    def test_manifest_cannot_authorise_a_customer_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.prepare(root, png_pixel(), 'exports/customer.png')
            result = scan_paths(root, [path])
            self.assertEqual([x['category'] for x in result], ['unapproved_visual'])

    def test_non_image_with_image_extension_is_rejected_even_if_fingerprinted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.prepare(root, b'This is a text export, not a PNG.')
            result = scan_paths(root, [path])
            self.assertEqual([x['category'] for x in result], ['invalid_visual_format'])
