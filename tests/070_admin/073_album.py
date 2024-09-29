from lotus.factories import AlbumFactory
from lotus.models import Album
from lotus.utils.tests import (
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
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
