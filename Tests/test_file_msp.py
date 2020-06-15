import pytest
from PIL import Image, MspImagePlugin

from .helper import assert_image_equal, extra_files, hopper

TEST_FILE = "Tests/images/hopper.msp"
EXTRA_DIR = "Tests/images/picins"
YA_EXTRA_DIR = "Tests/images/msp"


def test_sanity(tmp_path):
    test_file = str(tmp_path / "temp.msp")

    hopper("1").save(test_file)

    with Image.open(test_file) as im:
        im.load()
        assert im.mode == "1"
        assert im.size == (128, 128)
        assert im.format == "MSP"


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        MspImagePlugin.MspImageFile(invalid_file)


def test_bad_checksum():
    # Arrange
    # This was created by forcing Pillow to save with checksum=0
    bad_checksum = "Tests/images/hopper_bad_checksum.msp"

    # Act / Assert
    with pytest.raises(SyntaxError):
        MspImagePlugin.MspImageFile(bad_checksum)


def test_open_windows_v1():
    # Arrange
    # Act
    with Image.open(TEST_FILE) as im:

        # Assert
        assert_image_equal(im, hopper("1"))
        assert isinstance(im, MspImagePlugin.MspImageFile)


def _assert_file_image_equal(source_path, target_path):
    with Image.open(source_path) as im:
        with Image.open(target_path) as target:
            assert_image_equal(im, target)


@extra_files(EXTRA_DIR, ".msp")
def test_open_windows_v2(path):
    _assert_file_image_equal(path, path.replace(".msp", ".png"))


@extra_files(YA_EXTRA_DIR, ".MSP")
def test_msp_v2(path):
    _assert_file_image_equal(path, path.replace(".MSP", ".png"))


def test_cannot_save_wrong_mode(tmp_path):
    # Arrange
    im = hopper()
    filename = str(tmp_path / "temp.msp")

    # Act/Assert
    with pytest.raises(OSError):
        im.save(filename)
