import pytest
from PIL.Image import (
    FLIP_LEFT_RIGHT,
    FLIP_TOP_BOTTOM,
    ROTATE_90,
    ROTATE_180,
    ROTATE_270,
    TRANSPOSE,
    TRANSVERSE,
)

from . import helper
from .helper import assert_image_equal


@pytest.fixture(scope="module", params=("L", "RGB", "I;16", "I;16L", "I;16B"))
def im(request):
    im = helper.hopper(request.param).crop((0, 0, 121, 127)).copy()
    assert im.mode == request.param
    return im


def test_flip_left_right(im):
    mode = im.mode
    out = im.transpose(FLIP_LEFT_RIGHT)
    assert out.mode == mode
    assert out.size == im.size

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((x - 2, 1))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, 1))
    assert im.getpixel((1, y - 2)) == out.getpixel((x - 2, y - 2))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, y - 2))


def test_flip_top_bottom(im):
    mode = im.mode
    out = im.transpose(FLIP_TOP_BOTTOM)
    assert out.mode == mode
    assert out.size == im.size

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((1, y - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((x - 2, y - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((1, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((x - 2, 1))


def test_rotate_90(im):
    mode = im.mode
    out = im.transpose(ROTATE_90)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((1, x - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, 1))
    assert im.getpixel((1, y - 2)) == out.getpixel((y - 2, x - 2))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((y - 2, 1))


def test_rotate_180(im):
    mode = im.mode
    out = im.transpose(ROTATE_180)
    assert out.mode == mode
    assert out.size == im.size

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((x - 2, y - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, y - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((x - 2, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, 1))


def test_rotate_270(im):
    mode = im.mode
    out = im.transpose(ROTATE_270)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((y - 2, 1))
    assert im.getpixel((x - 2, 1)) == out.getpixel((y - 2, x - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((1, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, x - 2))


def test_transpose(im):
    mode = im.mode
    out = im.transpose(TRANSPOSE)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((1, 1))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, x - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((y - 2, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((y - 2, x - 2))


def test_tranverse(im):
    mode = im.mode
    out = im.transpose(TRANSVERSE)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((y - 2, x - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((y - 2, 1))
    assert im.getpixel((1, y - 2)) == out.getpixel((1, x - 2))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, 1))


def test_roundtrip(im):
    def transpose(first, second):
        return im.transpose(first).transpose(second)

    assert_image_equal(im, transpose(FLIP_LEFT_RIGHT, FLIP_LEFT_RIGHT))
    assert_image_equal(im, transpose(FLIP_TOP_BOTTOM, FLIP_TOP_BOTTOM))
    assert_image_equal(im, transpose(ROTATE_90, ROTATE_270))
    assert_image_equal(im, transpose(ROTATE_180, ROTATE_180))
    assert_image_equal(im.transpose(TRANSPOSE), transpose(ROTATE_90, FLIP_TOP_BOTTOM))
    assert_image_equal(im.transpose(TRANSPOSE), transpose(ROTATE_270, FLIP_LEFT_RIGHT))
    assert_image_equal(im.transpose(TRANSVERSE), transpose(ROTATE_90, FLIP_LEFT_RIGHT))
    assert_image_equal(im.transpose(TRANSVERSE), transpose(ROTATE_270, FLIP_TOP_BOTTOM))
    assert_image_equal(im.transpose(TRANSVERSE), transpose(ROTATE_180, TRANSPOSE))
