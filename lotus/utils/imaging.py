"""
=================
Imaging utilities
=================

"""
import io

from PIL import Image as PILimage
from PIL import ImageDraw as PILdrawer

from django.core.files import File


def create_image_file(filename=None, size=(100, 100), bg_color="blue",
                      text_color="white", text=None, format_name="PNG"):
    """
    Return a File object with a dummy generated image on the fly by PIL or
    possibly a SVG file.

    With default argument values the generated image will be a simple blue
    square in PNG with no text.

    Optionally, you can have any other supported format (JPEG, GIF, SVG), a custom
    background color and a text.

    Keyword Arguments:
        filename (string): Filename for created file, default to ``bg_color``
            value joined to extension with ``format`` value in lowercase (or
            ``jpg`` if format is ``JPEG``).
            Note than final filename may be different if all tests use the same
            one since Django will append a hash for uniqueness.
        format_name (string): Format name as available from PIL: ``JPEG``,
            ``PNG`` or ``GIF``. ``SVG`` format is also possible to create a
            dummy SVG file.
        size (tuple): A tuple of two integers respectively for width and height.
        bg_color (string): Color value to fill image, this should be a valid value
            for ``PIL.ImageColor``:
            https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
            or a valid HTML color name for SVG format. Default to "blue". WARNING: If
            you don't use named color (like "white" or "yellow"), you should give a
            custom filename to ``filename`` argument else the filename may be weird
            (like ``#111111.png``) or even fail (like with rgb color tuple).
        text_color (string): Color value for text. This should be a valid value
            for ``PIL.ImageColor``:
            https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
            Default to "white".
        text (string or boolean): ``True`` for automatic image size like
            320x240 (for ``320 `` width value and ``240`` height value). ``None`` or
            ``False`` to disable text drawing (this is the default value). A string for
            custom text, this should be a short text else it is not guaranteed to fit.

    Returns:
        django.core.files.File: File object.
    """
    file_extension = format_name.lower()
    # Enforce correct file extension depending format
    if file_extension == "jpeg":
        file_extension = "jpg"

    # NOTE: May validate if automatic formated filename from color only contains
    # alphanumeric characters to avoid failures with rgb(a) colors.
    filename = filename or "{}.{}".format(bg_color, file_extension)

    # Split given size
    width, height = size

    text_content = None
    # Format default text
    if text is True:
        # width x height
        text_content = "{}x{}".format(width, height)
    # Or just use possible given custom string
    elif isinstance(text, str):
        text_content = text

    # Manage correct mode depending format
    mode = "RGB"
    if format_name == "PNG":
        mode = "RGBA"

    # Create a SVG file
    if format_name == "SVG":
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg"'
            'role="img" aria-label="Placeholder"'
            'preserveAspectRatio="xMidYMid slice" focusable="false"'
            'viewBox="0 0 {width} {height}" style="text-anchor: middle">'
            '<rect width="100%" height="100%" fill="{bg_color}"></rect>'
            '<text x="50%" y="50%" fill="{text_color}" dy=".3em">{text}'
            '</text>'
            '</svg>'

        ).format(
            width=str(width),
            height=str(height),
            bg_color=bg_color,
            text=text_content,
            text_color=text_color,
        )
        output = io.StringIO(svg)
    # Create an image file for every other formats
    else:
        img = PILimage.new(mode, size, bg_color)
        # Optional text, always centered
        if text_content:
            draw = PILdrawer.Draw(img)
            text_width, text_height = draw.textsize(text_content)
            draw.text(
                (
                    (width - text_width) / 2,
                    (height - text_height) / 2
                ),
                text_content,
                fill=text_color,
            )

        output = io.BytesIO()
        img.save(output, format=format_name)

    return File(output, name=filename)
