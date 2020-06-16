import os

import pytest
from PIL import Image, ImageQt

from .helper import assert_image_equal, hopper

pytestmark = pytest.mark.skipif(
    not ImageQt.qt_is_installed, reason="Qt bindings are not installed"
)


@pytest.fixture(
    params=(None, "Tests/images/transparent.png", "Tests/images/7x13.png"),
    ids=lambda f: os.path.basename(f) if f else "hopper",
)
def test_image(request):
    if request.param:
        im = Image.open(request.param)
    else:
        im = hopper()
    try:
        yield im
    finally:
        im.close()


def roundtrip(expected):
    # PIL -> Qt
    intermediate = expected.toqimage()
    # Qt -> PIL
    result = ImageQt.fromqimage(intermediate)

    if intermediate.hasAlphaChannel():
        assert_image_equal(result, expected.convert("RGBA"))
    else:
        assert_image_equal(result, expected.convert("RGB"))


def test_sanity_1(test_image):
    roundtrip(test_image.convert("1"))


def test_sanity_rgb(test_image):
    roundtrip(test_image.convert("RGB"))


def test_sanity_rgba(test_image):
    roundtrip(test_image.convert("RGBA"))


def test_sanity_l(test_image):
    roundtrip(test_image.convert("L"))


def test_sanity_p(test_image):
    roundtrip(test_image.convert("P"))
