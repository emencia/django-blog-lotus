import io

from PIL import Image as PILimage
from PIL import ImageDraw

from django.core.files import File


class SampleImageCrafter:
    """
    Craft a basic sample image, either a bitmap or a SVG.

    Basically every supported format from PIL should work however this code only knows
    about JPEG, GIF, PNG and SVG.

    Keyword Arguments:
        font (Pil.ImageFont): A font object to use. This is only used for bitmap image.
            It is strongly recommended to use a TrueType font. Default is None, this
            will use the default PIL font. Note than text without a TrueType font will
            be badly positionned (almost centered but largely shifted).
    """
    def __init__(self, *args, **kwargs):
        self.font = None

        if "font" in kwargs:
            self.font = kwargs.pop("font")

    def get_text_content(self, text, width, height):
        """
        Get the text content to include in image.

        Arguments:
            text (string or boolean): Either a string to use it as content or ``True``
                to make automatic content from given sizes such as ``320x240`` (for
                width value ``320`` and height value ``240``). If string is given it
                should be a short text else it is not guaranteed to fit. If you don't
                want text content, just pass a empty string.
            width (integer): Width value to display in automatic text content.
            height (integer): Height value to display in automatic text content.

        Returns:
            string: Content to include in image.
        """
        text_content = ""

        # Format default text
        if text is True:
            # width x height
            text_content = "{}x{}".format(width, height)
        # Or just use possible given custom string
        elif isinstance(text, str):
            text_content = text

        return text_content

    def get_file_extension(self, format_name):
        """
        Get correct file extension depending format name.

        Arguments:
            format_name (string): The format name to use to get the right file
                extension. It could be any format supported. ``JPEG`` and ``JPG`` will
                traduces to ``jpg`` file extension.

        Returns:
            string: File extension without leading dot.
        """
        file_extension = format_name.lower()

        # "jpeg" is an allowed alias for "jpg"
        if file_extension == "jpeg":
            file_extension = "jpg"

        return file_extension

    def get_mode(self, format_name):
        """
        Get correct image color mode depending format name.

        Arguments:
            format_name (string): The format name to use to get the right file
                extension. It could be any format supported. ``PNG`` will be a ``RGBA``
                mode, every other format will be ``RGB``.

        Returns:
            string: Image color mode name.
        """
        if format_name == "PNG":
            return "RGBA"

        return "RGB"

    def get_filename(self, file_extension, filename=None, bg_color=None):
        """
        Get filename.

        Arguments:
            file_extension (string): File extension to use in automatic filename. Can
                be anything if ``filename`` argument is given since it will be ignored.

        Keyword Arguments:
            filename (string): Custom filename to use, every other arguments won't be
                used to compute filename.
            bg_color (string): A color name to use in automatic filename. For real, this
                can be anything since it is not validated.

        Returns:
            string: File name.
        """
        if not filename:
            return "{}.{}".format(bg_color, file_extension)

        return filename

    def build(self, filename=None, size=(100, 100), bg_color="blue", text_color="white",
              text=None, format_name="PNG"):
        """
        Build config for content creation

        Keyword Arguments:
            filename (string): Custom file name (with file extension) to override the
                automatic file name (based on other given arguments). Default is
                ``None`` which will produce an automatic file name.
            size (tuple): A tuple of two integers respectively for width and height.
                Default to ``(100, 100)`` which will produce a square of 100 pixels.
            bg_color (string): Color name to use to paint image background. Default to
                ``blue``.
            text_color (string): Color name to use to draw possible content text.
                Default to ``white``.
            text (string): Custom content text to include in image. Default to ``None``
                which will produce an automatic content based on size. Use an empty
                string to avoid content text in image.
            format_name (string): Image format name to use. Default to ``PNG``.

        Returns:
            dict: Configuration to use to create image file.
        """
        # Split given size
        width, height = size

        config = {
            "size": size,
            "width": width,
            "height": height,
            "format_name": format_name,
            "mode": self.get_mode(format_name),
            "file_extension": self.get_file_extension(format_name),
            "bg_color": bg_color,
            "text": text,
            "text_color": text_color,
            "text_content": self.get_text_content(text, width, height),
        }

        config["filename"] = self.get_filename(
            config["file_extension"],
            filename=filename,
            bg_color=config["bg_color"],
        )

        return config

    def create_vectorial(self, width, height, bg_color, text_content=None,
                         text_color=None):
        """
        Create SVG content.

        Arguments:
            width (integer): Image width.
            height (integer): Image height.
            bg_color (object): Color name to paint image background.

        Keyword Arguments:
            text_content (string): Content text to include instead of automatic content
                text.
            text_color (string): Color name to draw text instead of default one. It is
                required if you want to use the custom context text.

        Returns:
            io.StringIO: SVG content in a string buffer.
        """
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'role="img" aria-label="Placeholder" '
            'preserveAspectRatio="xMidYMid slice" focusable="false" '
            'viewBox="0 0 {width} {height}" style="text-anchor: middle">'
            '<rect width="100%" height="100%" fill="{bg_color}"></rect>'
        ).format(
            width=str(width),
            height=str(height),
            bg_color=bg_color,
        )

        if text_color and text_content:
            svg += (
                '<text x="50%" y="50%" fill="{text_color}" dy=".3em">{text}</text>'
            ).format(
                text=text_content,
                text_color=text_color,
            )

        svg += '</svg>'

        return io.StringIO(svg)

    def create_bitmap(self, mode, format_name, width, height, bg_color,
                      text_content=None, text_color=None):
        """
        Create Bitmap image object.

        Arguments:
            mode (string): Image color mode to use.
            format_name (string): Image format name to use.
            width (integer): Image width.
            height (integer): Image height.
            bg_color (object): Color name to paint image background.

        Keyword Arguments:
            text_content (string): Content text to include instead of automatic content
                text.
            text_color (string): Color name to draw text instead of default one. It is
                required if you want to use the custom context text.

        Returns:
            io.BytesIO: Image object in a byte buffer.
        """
        img = PILimage.new(mode, (width, height), bg_color)

        # Optional text, always centered
        if text_color and text_content:
            draw = ImageDraw.Draw(img)
            draw.text(
                (width / 2, height / 2),
                text_content,
                fill=text_color,
                font=self.font,
                anchor="mm",
            )

        output = io.BytesIO()
        img.save(output, format=format_name)

        return output

    def create(self, filename=None, size=(100, 100), bg_color="blue",
               text_color="white", text=None, format_name="PNG"):
        """
        Create an image inside a file object.

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
                Default to ``(100, 100)`` which will produce a square of 100 pixels.
            bg_color (string): Color value to fill image, this should be a valid value
                for ``PIL.ImageColor``:
                https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
                or a valid HTML color name for SVG format. Default to "blue". WARNING:
                If you don't use named color (like "white" or "yellow"), you should
                give a custom filename to ``filename`` argument else the filename may
                be weird (like ``#111111.png``).
            text_color (string): Color value for text. This should be a valid value
                for ``PIL.ImageColor``:
                https://pillow.readthedocs.io/en/stable/reference/ImageColor.html
                Default to "white".
            text (string or boolean): ``True`` for automatic image size like
                ``320x240`` (for width value ``320`` and height value ``240``). ``None``
                or ``False`` to disable text drawing (this is the default value). A
                string for custom text, this should be a short text else it is not
                guaranteed to fit.

        Returns:
            object: File object.
        """
        config = self.build(
            filename=filename,
            size=size,
            bg_color=bg_color,
            text_color=text_color,
            text=text,
            format_name=format_name
        )

        if config["format_name"] == "SVG":
            output = self.create_vectorial(
                config["width"],
                config["height"],
                config["bg_color"],
                text_content=config["text_content"],
                text_color=config["text_color"],
            )
        else:
            output = self.create_bitmap(
                config["mode"],
                config["format_name"],
                config["width"],
                config["height"],
                config["bg_color"],
                text_content=config["text_content"],
                text_color=config["text_color"],
            )

        return output


class DjangoSampleImageCrafter(SampleImageCrafter):
    """
    Alike SampleImageCrafter but return a Django File instead of a file object.
    """
    def create(self, *args, **kwargs):
        """
        Create an image inside a Django File object.

        Arguments:
            *args: The same positional arguments as from SampleImageCrafter.
            **kwargs: The same keyword arguments as from SampleImageCrafter.

        Returns:
            django.core.files.File: File object.
        """
        config = self.build(*args, **kwargs)

        if config["format_name"] == "SVG":
            output = self.create_vectorial(
                config["width"],
                config["height"],
                config["bg_color"],
                text_content=config["text_content"],
                text_color=config["text_color"],
            )
        else:
            output = self.create_bitmap(
                config["mode"],
                config["format_name"],
                config["width"],
                config["height"],
                config["bg_color"],
                text_content=config["text_content"],
                text_color=config["text_color"],
            )

        return File(output, name=config["filename"])
