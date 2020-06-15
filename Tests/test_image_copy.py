import copy

import pytest
from PIL import Image

from .helper import hopper


@pytest.mark.parametrize("mode", ("1", "P", "L", "RGB", "I", "F"))
def test_copy(mode):
    croppedCoordinates = (10, 10, 20, 20)
    croppedSize = (10, 10)

    # Internal copy method
    im = hopper(mode)
    out = im.copy()
    assert out.mode == im.mode
    assert out.size == im.size

    # Python's copy method
    im = hopper(mode)
    out = copy.copy(im)
    assert out.mode == im.mode
    assert out.size == im.size

    # Internal copy method on a cropped image
    im = hopper(mode)
    out = im.crop(croppedCoordinates).copy()
    assert out.mode == im.mode
    assert out.size == croppedSize

    # Python's copy method on a cropped image
    im = hopper(mode)
    out = copy.copy(im.crop(croppedCoordinates))
    assert out.mode == im.mode
    assert out.size == croppedSize


def test_copy_zero():
    im = Image.new("RGB", (0, 0))
    out = im.copy()
    assert out.mode == im.mode
    assert out.size == im.size
