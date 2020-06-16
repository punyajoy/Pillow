import math

import pytest
from PIL import Image, ImageTransform

from .helper import assert_image_equal, assert_image_similar, hopper


def test_sanity():
    im = Image.new("L", (100, 100))

    seq = tuple(range(10))

    transform = ImageTransform.AffineTransform(seq[:6])
    im.transform((100, 100), transform)
    transform = ImageTransform.ExtentTransform(seq[:4])
    im.transform((100, 100), transform)
    transform = ImageTransform.QuadTransform(seq[:8])
    im.transform((100, 100), transform)
    transform = ImageTransform.MeshTransform([(seq[:4], seq[:8])])
    im.transform((100, 100), transform)


def test_info():
    comment = b"File written by Adobe Photoshop\xa8 4.0"

    with Image.open("Tests/images/hopper.gif") as im:
        assert im.info["comment"] == comment

        transform = ImageTransform.ExtentTransform((0, 0, 0, 0))
        new_im = im.transform((100, 100), transform)
    assert new_im.info["comment"] == comment


def test_extent():
    im = hopper("RGB")
    (w, h) = im.size
    # fmt: off
    transformed = im.transform(im.size, Image.EXTENT,
                               (0, 0,
                                w//2, h//2),  # ul -> lr
                               Image.BILINEAR)
    # fmt: on

    scaled = im.resize((w * 2, h * 2), Image.BILINEAR).crop((0, 0, w, h))

    # undone -- precision?
    assert_image_similar(transformed, scaled, 23)


def test_quad():
    # one simple quad transform, equivalent to scale & crop upper left quad
    im = hopper("RGB")
    (w, h) = im.size
    # fmt: off
    transformed = im.transform(im.size, Image.QUAD,
                               (0, 0, 0, h//2,
                                # ul -> ccw around quad:
                                w//2, h//2, w//2, 0),
                               Image.BILINEAR)
    # fmt: on

    scaled = im.transform((w, h), Image.AFFINE, (0.5, 0, 0, 0, 0.5, 0), Image.BILINEAR)

    assert_image_equal(transformed, scaled)


@pytest.mark.parametrize(
    "mode,pixel",
    (("RGB", (255, 0, 0)), ("RGBA", (255, 0, 0, 255)), ("LA", (76, 0)),),
    ids=("RGB", "RGBA", "LA"),
)
def test_fill(mode, pixel):
    im = hopper(mode)
    (w, h) = im.size
    transformed = im.transform(
        im.size, Image.EXTENT, (0, 0, w * 2, h * 2), Image.BILINEAR, fillcolor="red",
    )

    assert transformed.getpixel((w - 1, h - 1)) == pixel


def test_mesh():
    # this should be a checkerboard of halfsized hoppers in ul, lr
    im = hopper("RGBA")
    (w, h) = im.size
    # fmt: off
    transformed = im.transform(im.size, Image.MESH,
                               [((0, 0, w//2, h//2),  # box
                                (0, 0, 0, h,
                                 w, h, w, 0)),  # ul -> ccw around quad
                                ((w//2, h//2, w, h),  # box
                                (0, 0, 0, h,
                                 w, h, w, 0))],  # ul -> ccw around quad
                               Image.BILINEAR)
    # fmt: on

    scaled = im.transform(
        (w // 2, h // 2), Image.AFFINE, (2, 0, 0, 0, 2, 0), Image.BILINEAR
    )

    checker = Image.new("RGBA", im.size)
    checker.paste(scaled, (0, 0))
    checker.paste(scaled, (w // 2, h // 2))

    assert_image_equal(transformed, checker)

    # now, check to see that the extra area is (0, 0, 0, 0)
    blank = Image.new("RGBA", (w // 2, h // 2), (0, 0, 0, 0))

    assert_image_equal(blank, transformed.crop((w // 2, 0, w, h // 2)))
    assert_image_equal(blank, transformed.crop((0, h // 2, w // 2, h)))


@pytest.mark.parametrize(
    "op",
    [
        lambda im, sz: im.resize(sz, Image.BILINEAR),
        lambda im, sz: im.transform(sz, Image.EXTENT, (0, 0, *im.size), Image.BILINEAR),
    ],
    ids=["resize", "transform"],
)
def test_alpha_premult(op):
    # create image with half white, half black,
    # with the black half transparent.
    # do op,
    # there should be no darkness in the white section.
    im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    im2 = Image.new("RGBA", (5, 10), (255, 255, 255, 255))
    im.paste(im2, (0, 0))

    im = op(im, (40, 10))
    im_background = Image.new("RGB", (40, 10), (255, 255, 255))
    im_background.paste(im, (0, 0), im)

    hist = im_background.histogram()
    assert 40 * 10 == hist[-1]


def test_blank_fill():
    # attempting to hit
    # https://github.com/python-pillow/Pillow/issues/254 reported
    #
    # issue is that transforms with transparent overflow area
    # contained junk from previous images, especially on systems with
    # constrained memory. So, attempt to fill up memory with a
    # pattern, free it, and then run the mesh test again. Using a 1Mp
    # image with 4 bands, for 4 megs of data allocated, x 64. OMM (64
    # bit 12.04 VM with 512 megs available, this fails with Pillow <
    # a0eaf06cc5f62a6fb6de556989ac1014ff3348ea
    #
    # Running by default, but I'd totally understand not doing it in
    # the future

    pattern = [Image.new("RGBA", (1024, 1024), (a, a, a, a)) for a in range(1, 65)]

    # Yeah. Watch some JIT optimize this out.
    pattern = None  # noqa: F841

    test_mesh()


def test_missing_method_data():
    with hopper() as im:
        with pytest.raises(ValueError):
            im.transform((100, 100), None)


def test_unknown_resampling_filter():
    with hopper() as im:
        (w, h) = im.size
        for resample in (Image.BOX, "unknown"):
            with pytest.raises(ValueError):
                im.transform((100, 100), Image.EXTENT, (0, 0, w, h), resample)


@pytest.fixture()
def image():
    """Test image for test_rotate, test_resize, and test_traslate"""
    im = hopper("RGB")
    return im.crop((10, 20, im.width - 10, im.height - 20))


@pytest.fixture(
    scope="module",
    params=[Image.AFFINE, Image.PERSPECTIVE],
    ids=("affine", "perspective"),
)
def transform(request):
    """Image transform for test_rotate, test_resize, and test_traslate"""
    return request.param


@pytest.mark.parametrize(
    "deg,transpose",
    (
        (0, None),
        (90, Image.ROTATE_90),
        (180, Image.ROTATE_180),
        (270, Image.ROTATE_270),
    ),
    ids=("0", "90", "180", "270"),
)
def test_rotate(deg, transpose, image, transform):
    im = image

    angle = -math.radians(deg)
    matrix = [
        round(math.cos(angle), 15),
        round(math.sin(angle), 15),
        0.0,
        round(-math.sin(angle), 15),
        round(math.cos(angle), 15),
        0.0,
        0,
        0,
    ]
    matrix[2] = (1 - matrix[0] - matrix[1]) * im.width / 2
    matrix[5] = (1 - matrix[3] - matrix[4]) * im.height / 2

    if transpose is not None:
        transposed = im.transpose(transpose)
    else:
        transposed = im

    for resample in [Image.NEAREST, Image.BILINEAR, Image.BICUBIC]:
        transformed = im.transform(transposed.size, transform, matrix, resample)
        assert_image_equal(transposed, transformed)


@pytest.mark.parametrize(
    "scale,epsilonscale",
    ((1.1, 6.9), (1.5, 5.5), (2.0, 5.5), (2.3, 3.7), (2.5, 3.7)),
    ids=("1.1", "1.5", "2.0", "2.3", "2.5"),
)
def test_resize(scale, epsilonscale, image, transform):
    im = image

    size_up = int(round(im.width * scale)), int(round(im.height * scale))
    matrix_up = [1 / scale, 0, 0, 0, 1 / scale, 0, 0, 0]
    matrix_down = [scale, 0, 0, 0, scale, 0, 0, 0]

    for resample, epsilon in [
        (Image.NEAREST, 0),
        (Image.BILINEAR, 2),
        (Image.BICUBIC, 1),
    ]:
        transformed = im.transform(size_up, transform, matrix_up, resample)
        transformed = transformed.transform(im.size, transform, matrix_down, resample)
        assert_image_similar(transformed, im, epsilon * epsilonscale)


@pytest.mark.parametrize(
    "x,y,epsilonscale",
    ((0.1, 0, 3.7), (0.6, 0, 9.1), (50, 50, 0)),
    ids=("0.1", "0.6", "50"),
)
def test_translate(x, y, epsilonscale, image, transform):
    im = image

    size_up = int(round(im.width + x)), int(round(im.height + y))
    matrix_up = [1, 0, -x, 0, 1, -y, 0, 0]
    matrix_down = [1, 0, x, 0, 1, y, 0, 0]

    for resample, epsilon in [
        (Image.NEAREST, 0),
        (Image.BILINEAR, 1.5),
        (Image.BICUBIC, 1),
    ]:
        transformed = im.transform(size_up, transform, matrix_up, resample)
        transformed = transformed.transform(im.size, transform, matrix_down, resample)
        assert_image_similar(transformed, im, epsilon * epsilonscale)
