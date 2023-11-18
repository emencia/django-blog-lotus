from pathlib import Path

import pytest

from django.core.exceptions import ValidationError

from lotus.factories import (
    AlbumFactory, AlbumItemFactory
)
from lotus.models import Album, AlbumItem
from lotus.utils.imaging import DjangoSampleImageCrafter


def test_album_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    album = Album(
        title="Bar",
    )
    album.full_clean()
    album.save()

    assert Album.objects.filter(title="Bar").count() == 1
    assert "Bar" == album.title


def test_album_required_fields(db):
    """
    Basic model validation with missing required fields should fail
    """
    album = Album()

    with pytest.raises(ValidationError) as excinfo:
        album.full_clean()

    assert excinfo.value.message_dict == {
        "title": ["This field cannot be blank."],
    }


def test_album_creation(db):
    """
    Factory should correctly create a new object without any errors.
    """
    album = AlbumFactory(title="foo")
    assert album.title == "foo"


def test_albumitem_basic(db):
    """
    Basic model saving with required fields should not fail.
    """
    crafter = DjangoSampleImageCrafter()

    album = AlbumFactory()

    item = AlbumItem(
        album=album,
        media=crafter.create(filename="machin.png"),
    )
    item.full_clean()
    item.save()

    assert Album.objects.filter(title=album.title).count() == 1
    assert AlbumItem.objects.filter(album=album).count() == 1


def test_albumitem_required_fields(db):
    """
    Basic model validation with missing required fields should fail.
    """
    item = AlbumItem()

    with pytest.raises(ValidationError) as excinfo:
        item.full_clean()

    assert excinfo.value.message_dict == {
        "album": ["This field cannot be null."],
        "media": ["This field cannot be blank."],
    }


def test_albumitem_creation(db):
    """
    Factory should correctly create a new object without any errors.
    """
    item = AlbumItemFactory(title="foo")
    assert item.title == "foo"


def test_album_fill_items(db):
    """
    Album factory post generation method "fill_item" should fill some items from
    given argument.
    """
    album = AlbumFactory(title="foo", fill_items=True)
    assert album.albumitems.count() == 1

    album = AlbumFactory(title="foo", fill_items=3)
    assert album.albumitems.count() == 3


def test_albumitem_model_file_purge(db):
    """
    AlbumItem 'media' field file should follow correct behaviors:

    * When object is deleted, its files should be delete from filesystem too;
    * When changing file from an object, its previous files (if any) should be
      deleted;
    """
    crafter = DjangoSampleImageCrafter()

    album = AlbumFactory()

    ping = AlbumItemFactory(
        album=album,
        media=crafter.create(filename="machin.png")
    )
    pong = AlbumItemFactory(
        album=album,
        media=crafter.create(filename="machin.png")
    )

    # Memorize some data to use after deletion
    ping_path = ping.media.path
    pong_path = pong.media.path

    # Delete object
    ping.delete()

    # File is deleted along its object
    assert Path(ping_path).exists() is False
    # Paranoiac mode: other existing similar filename (as uploaded) are conserved
    # since Django rename file with a unique hash if filename alread exist, they
    # should not be mistaken
    assert Path(pong_path).exists() is True

    # Change object file to a new one
    pong.media = crafter.create(filename="new.png")
    pong.save()

    # During pre save signal, old file is removed from FS and new one is left
    # untouched
    assert Path(pong_path).exists() is False
    assert Path(pong.media.path).exists() is True


def test_album_model_file_purge(db):
    """
    When an Album is deleted, its item are removed and their files also.
    """
    crafter = DjangoSampleImageCrafter()

    album = AlbumFactory()

    ping = AlbumItemFactory(
        album=album,
        media=crafter.create(filename="machin.png")
    )

    # Memorize some data to use after deletion
    ping_path = ping.media.path

    # Delete object
    album.delete()

    # File is deleted along its object
    assert Path(ping_path).exists() is False
