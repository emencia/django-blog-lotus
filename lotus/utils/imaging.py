# -*- coding: utf-8 -*-
import io

from PIL import Image as PILimage

from django.core.files import File


def create_image_file(filename=None, size=(100, 100), color="blue",
                      format_name="PNG"):
    """
    Return a File object with a dummy generated image on the fly by PIL or
    possibly a SVG file.

    With default argument values the generated image will be a simple blue
    square in PNG.

    Keyword Arguments:
        filename (string): Filename for created file, default to ``color``
            value joined to extension with ``format`` value in lowercase (or
            ``jpg`` if format is ``JPEG``).
            Note than final filename may be different if all tests use the same
            one since Django will append a hash for uniqueness.
        format_name (string): Format name as available from PIL: ``JPEG``,
            ``PNG`` or ``GIF``. ``SVG`` format is also possible to create a
            dummy SVG file.
        size (tuple): A tuple of two integers respectively for width and height.
        color (string): Color value to fill image, this should be a valid value
            for ``PIL.ImageColor``:
            https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
            or a valid HTML color name for SVG format.

    Returns:
        django.core.files.File: File object.
    """
    ext = format_name.lower()
    # Enforce correct file extension depending format
    if ext == "jpeg":
        ext = "jpg"

    filename = filename or "{}.{}".format(color, ext)

    # Manage correct mode depending format
    mode = "RGB"
    if format_name == "PNG":
        mode = "RGBA"

    # Create a SVG file
    if format_name == 'SVG':
        width, height = size
        html = (
            """<svg xmlns="http://www.w3.org/2000/svg" """
            """viewBox="0 0 {width} {height}">"""
            """<path fill="{color}" d="M0 0h{width}v{height}H0z"/>"""
            """</svg>"""
        ).format(
            width=str(width),
            height=str(height),
            color=color,
        )
        thumb_io = io.StringIO(html)
    # Create an image file for every other formats
    else:
        thumb = PILimage.new(mode, size, color)
        thumb_io = io.BytesIO()
        thumb.save(thumb_io, format=format_name)

    return File(thumb_io, name=filename)
