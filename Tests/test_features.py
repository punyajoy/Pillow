from __future__ import unicode_literals

import io
import os

from PIL import features

from .helper import PillowTestCase, unittest

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False

os.environ.setdefault("CI_FEATURES", "")


class TestFeatures(PillowTestCase):
    def test_check(self):
        # Check every check_xxx function returns a boolean
        # Check the correctness of the convenience function
        for module in features.modules:
            self.assertIn(features.check_module(module), [True, False])
            self.assertEqual(features.check_module(module), features.check(module))
        for codec in features.codecs:
            self.assertIn(features.check_codec(codec), [True, False])
            self.assertEqual(features.check_codec(codec), features.check(codec))
        for feature in features.features:
            self.assertIn(features.check_feature(feature), [True, False])
            self.assertEqual(features.check_feature(feature), features.check(feature))

    @unittest.skipUnless(HAVE_WEBP, "WebP not available")
    def test_webp_transparency(self):
        self.assertEqual(
            features.check("transp_webp"), not _webp.WebPDecoderBuggyAlpha()
        )
        self.assertEqual(features.check("transp_webp"), _webp.HAVE_TRANSPARENCY)

    @unittest.skipUnless(HAVE_WEBP, "WebP not available")
    def test_webp_mux(self):
        self.assertEqual(features.check("webp_mux"), _webp.HAVE_WEBPMUX)

    @unittest.skipUnless(HAVE_WEBP, "WebP not available")
    def test_webp_anim(self):
        self.assertEqual(features.check("webp_anim"), _webp.HAVE_WEBPANIM)

    def test_supported(self):
        self.assertIsInstance(features.get_supported_modules(), list)
        self.assertIsInstance(features.get_supported_codecs(), list)
        self.assertIsInstance(features.get_supported_features(), list)
        self.assertIsInstance(features.get_supported(), list)

    @unittest.skipUnless("CI_FEATURES" in os.environ, "CI_FEATURES not set")
    def test_supported_ci(self):
        self.assertEqual(
            features.get_supported().sort(), os.environ["CI_FEATURES"].split(",").sort()
        )

    def test_check_unsupported(self):
        self.assertRaises(ValueError, features.check_codec, "unsupported")
        self.assertRaises(ValueError, features.check_module, "unsupported")
        self.assertRaises(ValueError, features.check_feature, "unsupported")
        # self.assertRaises(ValueError, features.check, "unsupported")

    def test_pilinfo(self):
        buf = io.StringIO()
        features.pilinfo(buf)
        out = buf.getvalue()
        lines = out.splitlines()
        self.assertEqual(lines[0], "-" * 68)
        self.assertTrue(lines[1].startswith("Pillow "))
        self.assertEqual(lines[2], "-" * 68)
        self.assertTrue(lines[3].startswith("Python modules loaded from "))
        self.assertTrue(lines[4].startswith("Binary modules loaded from "))
        self.assertEqual(lines[5], "-" * 68)
        self.assertTrue(lines[6].startswith("Python "))
        jpeg = (
            "\n"
            + "-" * 68
            + "\n"
            + "JPEG image/jpeg\n"
            + "Extensions: .jfif, .jpe, .jpeg, .jpg\n"
            + "Features: open, save\n"
            + "-" * 68
            + "\n"
        )
        self.assertIn(jpeg, out)
