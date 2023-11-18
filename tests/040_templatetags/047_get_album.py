import pytest

from django.template import TemplateSyntaxError

from lotus.factories import AlbumFactory
from lotus.templatetags.lotus import get_album_html
from lotus.utils.tests import html_pyquery


def test_argument_album_type(db):
    """
    Tag only expect an Album object in 'album' argument.
    """
    with pytest.raises(TemplateSyntaxError) as excinfo:
        get_album_html({}, "foo")

    assert str(excinfo.value) == (
        "'get_album_html' tag only accepts an Album object as 'album' argument. "
        "Object type 'str' was given."
    )


def test_empty_album(db):
    """
    Tag should not fail when album is empty.
    """
    album = AlbumFactory()

    rendered = get_album_html({}, album)
    dom = html_pyquery(rendered)

    album_title = dom.find(".title")[0]
    assert album_title.text == album.title

    album_items = dom.find(".albumitems > .item")
    assert album_items == []


def test_album_render(db):
    """
    Tag should list all item from an Album in the right order.
    """
    album = AlbumFactory(fill_items=2)

    rendered = get_album_html({}, album)
    dom = html_pyquery(rendered)

    album_title = dom.find(".title")[0]
    assert album_title.text == album.title

    rendered_items = [
        (
            item.cssselect(".title")[0].text,
            item.cssselect("a")[0].get("href"),
        )
        for item in dom.find(".albumitems .item")
    ]

    expected_items = [
        (item.title, item.media.url)
        for item in album.albumitems.all()
    ]

    assert rendered_items == expected_items
