import pytest

from lotus.utils.imaging import SampleImageCrafter, DjangoSampleImageCrafter
from lotus.utils.tests import sum_file_object


@pytest.mark.parametrize("format_name, expected", [
    ("jpg", "jpg"),
    ("jpeg", "jpg"),
    ("JPEG", "jpg"),
    ("PNG", "png"),
])
def test_imagecrafter_file_extension(format_name, expected):
    """
    Method should returns the right file extension more according to given format.
    """
    builder = SampleImageCrafter()
    assert builder.get_file_extension(format_name) == expected


@pytest.mark.parametrize("format_name, expected", [
    ("gif", "RGB"),
    ("jpg", "RGB"),
    ("jpeg", "RGB"),
    ("JPEG", "RGB"),
    ("PNG", "RGBA"),
])
def test_imagecrafter_mode(format_name, expected):
    """
    Method should returns the right mode according to given format.
    """
    builder = SampleImageCrafter()
    assert builder.get_mode(format_name) == expected


@pytest.mark.parametrize("file_extension, options, expected", [
    (
        "gif",
        {},
        "None.gif",
    ),
    (
        "png",
        {"bg_color": "ping"},
        "ping.png",
    ),
    (
        "png",
        {"bg_color": "#f0f0f0"},
        "#f0f0f0.png",
    ),
    (
        "png",
        {"bg_color": "ping", "filename": "foobar.txt"},
        "foobar.txt",
    ),
])
def test_imagecrafter_filename(file_extension, options, expected):
    """
    Method should returns the right filename according to given options.
    """
    builder = SampleImageCrafter()
    assert builder.get_filename(file_extension, **options) == expected


@pytest.mark.parametrize("text, width, height, expected", [
    (
        "Hello world",
        120,
        60,
        "Hello world",
    ),
    (
        None,
        120,
        60,
        "",
    ),
    (
        False,
        120,
        60,
        "",
    ),
    (
        True,
        120,
        60,
        "120x60",
    ),
])
def test_imagecrafter_text_content(text, width, height, expected):
    """
    Method should returns the right text content according to options.
    """
    builder = SampleImageCrafter()
    assert builder.get_text_content(text, width, height) == expected


@pytest.mark.parametrize("options, expected", [
    (
        {},
        {
            "size": (100, 100),
            "width": 100,
            "height": 100,
            "format_name": "PNG",
            "mode": "RGBA",
            "file_extension": "png",
            "bg_color": "blue",
            "text": None,
            "text_color": "white",
            "text_content": "",
            "filename": "blue.png"
        }
    ),
    (
        {
            "size": (320, 240),
            "filename": "foobar.jpeg",
            "bg_color": "pink",
            "text_color": "black",
            "text": "Hello World!",
            "format_name": "JPEG",
        },
        {
            "size": (320, 240),
            "width": 320,
            "height": 240,
            "format_name": "JPEG",
            "mode": "RGB",
            "file_extension": "jpg",
            "bg_color": "pink",
            "text": "Hello World!",
            "text_color": "black",
            "text_content": "Hello World!",
            "filename": "foobar.jpeg"
        }
    ),
])
def test_imagecrafter_build(options, expected):
    """
    Method should build correction configuration according to options.
    """
    builder = SampleImageCrafter()
    assert builder.build(**options) == expected


@pytest.mark.parametrize("width, height, bg_color, options, file_expection", [
    (
        320,
        240,
        "cyan",
        {},
        "cyan_without_text.svg"
    ),
    (
        320,
        240,
        "burlywood",
        {
            "text_content": "Hello World!",
            "text_color": "black",
        },
        "burlywood_with_text.svg"
    ),
])
def test_imagecrafter_create_vectorial(tests_settings, width, height, bg_color, options,
                                       file_expection):
    """
    Method should creates the right SVG file according to given options.
    """
    builder = SampleImageCrafter()
    built = builder.create_vectorial(width, height, bg_color, **options)
    content = built.read()

    sample = tests_settings.fixtures_path / "image_samples" / file_expection

    # NOTE: Used to automatically save built sample, this is not something to keep
    # enabled
    # if not sample.exists():
    #     sample.write_text(content)

    sample_content = sample.read_text()

    assert content == sample_content


@pytest.mark.parametrize(
    "mode, format_name, width, height, bg_color, options, file_expection",
    [
        (
            "RGBA",
            "PNG",
            320,
            240,
            "cyan",
            {},
            "cyan_without_text.png"
        ),
        (
            "RGBA",
            "PNG",
            320,
            240,
            "burlywood",
            {
                "text_content": "Hello World!",
                "text_color": "black",
            },
            "burlywood_with_text.png"
        ),
    ]
)
def test_imagecrafter_create_bitmap(tests_settings, font, mode, format_name,
                                    width, height, bg_color, options, file_expection):
    """
    Method should creates the right bitmap file according to given options.
    """
    builder = SampleImageCrafter(font=font)
    built = builder.create_bitmap(mode, format_name, width, height, bg_color, **options)
    built_hash = sum_file_object(built)

    sample = tests_settings.fixtures_path / "image_samples" / file_expection

    # NOTE: Used to automatically save built sample, this is not something to keep
    # enabled
    # if not sample.exists():
    #     with sample.open("wb") as sample_file:
    #         sample_file.write(built.getvalue())

    with sample.open("rb") as sample_file:
        sample_hash = sum_file_object(sample_file)

    assert built_hash == sample_hash


@pytest.mark.parametrize("options, file_expection", [
    (
        {},
        "default.png",
    ),
    (
        {
            "filename": "burlywood_with_text.svg",
            "size": (320, 240),
            "bg_color": "burlywood",
            "text": "Hello World!",
            "text_color": "black",
            "format_name": "SVG",
        },
        "burlywood_with_text.svg"
    ),
])
def test_imagecrafter_create(tests_settings, font, options, file_expection):
    """
    Method should creates the right image file object according to given options.
    """
    builder = SampleImageCrafter(font=font)
    built = builder.create(**options)
    sample = tests_settings.fixtures_path / "image_samples" / file_expection

    # For SVG just read them as text
    if options.get("format_name") == "SVG":
        built_hash = built.read()
        sample_hash = sample.read_text()
    # Only compute hash with bitmaps
    else:
        built_hash = sum_file_object(built)
        with sample.open("rb") as sample_file:
            sample_hash = sum_file_object(sample_file)

    assert built_hash == sample_hash


@pytest.mark.parametrize("options, file_expection", [
    (
        {},
        "default.png",
    ),
    (
        {
            "filename": "burlywood_with_text.svg",
            "size": (320, 240),
            "bg_color": "burlywood",
            "text": "Hello World!",
            "text_color": "black",
            "format_name": "SVG",
        },
        "burlywood_with_text.svg"
    ),
])
def test_djangoimagecrafter_create(tests_settings, font, options, file_expection):
    """
    Method should creates the right Django file object according to given options.
    """
    builder = DjangoSampleImageCrafter(font=font)
    built = builder.create(**options)
    sample = tests_settings.fixtures_path / "image_samples" / file_expection

    # For SVG just read them as text
    if options.get("format_name") == "SVG":
        built_hash = built.file.read()
        sample_hash = sample.read_text()
    # Only compute hash with bitmaps
    else:
        built_hash = sum_file_object(built.file)
        with sample.open("rb") as sample_file:
            sample_hash = sum_file_object(sample_file)

    assert built_hash == sample_hash


@pytest.mark.skip("font family management with image creation from demo maker")
def test_porting_new_create_bitmap():
    """
    TODO:

    This test to remind the lotus_demo command do not use yet the font argument from
    DjangoSampleImageCrafter since it needs the font that is embedded in test structure
    that is not shipped in package.

    The font has to be located in application to be packaged and available out of the
    development environment.

    This is probably to fix font size in image to better fit on lowest breakpoints,
    or maybe the demo command is broken because it use it, i can not remember exactly
    yet..
    """
    assert 1 == 42
