from lotus.factories import AlbumFactory
from lotus.forms import AlbumAdminForm
from lotus.models import Album
from lotus.utils.tests import (
    build_post_data_from_object, get_admin_add_url, get_admin_change_url,
    get_admin_list_url,
)


def test_album_admin_add(db, admin_client):
    """
    Album model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(Album)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_album_admin_list(db, admin_client):
    """
    Album model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(Album)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_album_admin_detail(db, admin_client):
    """
    Album model admin detail view should not raise error on GET request.
    """
    obj = AlbumFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_album_admin_change_form(db, admin_client):
    """
    Ensure the admin change form is working well (this should media add form
    also) and ensure image upload is correct.
    """
    # Create new object without a media file
    obj = AlbumFactory.build()

    # Build initial POST data
    ignore = ["id"]
    data = build_post_data_from_object(Album, obj, ignore=ignore)
    file_data = {}

    f = AlbumAdminForm(data, file_data, instance=obj)

    # No validation errors
    assert f.is_valid() is True
    assert f.errors.as_data() == {}

    updated_obj = f.save()

    # Check everything has been saved
    assert updated_obj.title == obj.title

    assert Album.objects.count() == 1
