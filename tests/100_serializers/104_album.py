import datetime
import json

import pytest
from freezegun import freeze_time

try:
    from rest_framework.test import APIRequestFactory
    from rest_framework.renderers import JSONRenderer
    from lotus.serializers import AlbumSerializer
except ModuleNotFoundError:
    APIRequestFactory, JSONRenderer = None, None
    API_AVAILABLE = False
else:
    API_AVAILABLE = True

from lotus.compat.import_zoneinfo import ZoneInfo
from lotus.factories import AlbumFactory, AlbumItemFactory


pytestmark = pytest.mark.skipif(
    not API_AVAILABLE,
    reason="Django REST is not available, API is disabled"
)


@freeze_time("2012-10-15 10:00:00")
def test_album_complete_serializer(db, api_client):
    """
    Serializer 'AuthorSerializer' should returns the full payload as expected.
    """
    # Build a dummy request, we don't care about requested URL.
    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object
    serialized = AlbumSerializer(None)
    assert serialized.data == {"title": ""}

    album = AlbumFactory(title="Filled with 2 items")
    item_1 = AlbumItemFactory(album=album)
    item_2 = AlbumItemFactory(album=album)

    serialized = AlbumSerializer(album, context={
        "request": request,
        "lotus_now": datetime.datetime(2012, 10, 15, 10, 00).replace(
            tzinfo=ZoneInfo("UTC")
        ),
        "LANGUAGE_CODE": "en",
    })

    assert json.loads(JSONRenderer().render(serialized.data)) == {
        "items": [
            {
                "modified": "2012-10-15T12:00:00+02:00",
                "title": item_1.title,
                "order": item_1.order,
                "media": "http://testserver" + item_1.media.url,
            },
            {
                "modified": "2012-10-15T12:00:00+02:00",
                "title": item_2.title,
                "order": item_2.order,
                "media": "http://testserver" + item_2.media.url,
            },
        ],
        "title": album.title,
        "modified": "2012-10-15T12:00:00+02:00",
    }
