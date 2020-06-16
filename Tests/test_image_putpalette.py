import pytest
from PIL import ImagePalette

from .helper import hopper


@pytest.mark.parametrize(
    "mode,expected", (("L", "P"), ("LA", "PA"), ("P", "P"), ("PA", "PA")),
)
def test_putpalette_valid(mode, expected):
    im = hopper(mode).copy()
    im.putpalette(list(range(256)) * 3)
    p = im.getpalette()
    assert im.mode == expected
    assert p[:10] == list(range(10))


@pytest.mark.parametrize(
    "mode", ("1", "I", "F", "RGB", "RGBA", "YCbCr"),
)
def test_putpalette_invalid(mode):
    with pytest.raises(ValueError):
        im = hopper(mode).copy()
        im.putpalette(list(range(256)) * 3)
        im.getpalette()
        im.mode


def test_imagepalette():
    im = hopper("P")
    im.putpalette(ImagePalette.negative())
    im.putpalette(ImagePalette.random())
    im.putpalette(ImagePalette.sepia())
    im.putpalette(ImagePalette.wedge())
