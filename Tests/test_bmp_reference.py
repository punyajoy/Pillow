import os

import pytest
from PIL import Image

from .helper import assert_image_similar

base = os.path.join("Tests", "images", "bmp")


def get_files(d, ext=".bmp"):
    return [
        os.path.join(base, d, f) for f in os.listdir(os.path.join(base, d)) if ext in f
    ]


@pytest.mark.parametrize("f", get_files("b"), ids=os.path.basename)
def test_bad(f):
    """ These shouldn't crash/dos, but they shouldn't return anything
    either """
    with pytest.warns(None) as raised:
        try:
            with Image.open(f) as im:
                im.load()
        except Exception:  # as msg:
            pass

    # Assert that there is no unclosed file warning
    assert not raised


@pytest.mark.parametrize("f", get_files("q"), ids=os.path.basename)
def test_questionable(f):
    """ These shouldn't crash/dos, but it's not well defined that these
    are in spec """
    supported = [
        "pal8os2v2.bmp",
        "rgb24prof.bmp",
        "pal1p1.bmp",
        "pal8offs.bmp",
        "rgb24lprof.bmp",
        "rgb32fakealpha.bmp",
        "rgb24largepal.bmp",
        "pal8os2sp.bmp",
        "rgb32bf-xbgr.bmp",
    ]
    try:
        with Image.open(f) as im:
            im.load()
        if os.path.basename(f) not in supported:
            print("Please add %s to the partially supported bmp specs." % f)
    except Exception:  # as msg:
        if os.path.basename(f) in supported:
            raise


@pytest.mark.parametrize("f", get_files("g"), ids=os.path.basename)
def test_good(f):
    """ These should all work. There's a set of target files in the
    html directory that we can compare against. """

    # Target files, if they're not just replacing the extension
    file_map = {
        "pal1wb.bmp": "pal1.png",
        "pal4rle.bmp": "pal4.png",
        "pal8-0.bmp": "pal8.png",
        "pal8rle.bmp": "pal8.png",
        "pal8topdown.bmp": "pal8.png",
        "pal8nonsquare.bmp": "pal8nonsquare-v.png",
        "pal8os2.bmp": "pal8.png",
        "pal8os2sp.bmp": "pal8.png",
        "pal8os2v2.bmp": "pal8.png",
        "pal8os2v2-16.bmp": "pal8.png",
        "pal8v4.bmp": "pal8.png",
        "pal8v5.bmp": "pal8.png",
        "rgb16-565pal.bmp": "rgb16-565.png",
        "rgb24pal.bmp": "rgb24.png",
        "rgb32.bmp": "rgb24.png",
        "rgb32bf.bmp": "rgb24.png",
    }

    try:
        with Image.open(f) as im:
            im.load()

            # get comparison image
            compare = os.path.split(f)[1]
            if compare in file_map:
                compare = os.path.join(base, "html", file_map[compare])
            else:
                compare = os.path.splitext(compare)[0]
                compare = os.path.join(base, "html", "%s.png" % compare)

            with Image.open(compare) as compare:
                compare.load()
                if im.mode == "P":
                    # assert image similar doesn't really work
                    # with paletized image, since the palette might
                    # be differently ordered for an equivalent image.
                    im = im.convert("RGBA")
                    compare = im.convert("RGBA")
                assert_image_similar(im, compare, 5)

    except Exception as msg:
        # there are three here that are unsupported:
        unsupported = (
            os.path.join(base, "g", "rgb32bf.bmp"),
            os.path.join(base, "g", "pal8rle.bmp"),
            os.path.join(base, "g", "pal4rle.bmp"),
        )
        assert f in unsupported, "Unsupported Image {}: {}".format(f, msg)
