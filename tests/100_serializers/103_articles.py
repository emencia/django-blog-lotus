import datetime
import json

from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.conf import settings

from rest_framework.test import APIRequestFactory
from rest_framework.renderers import JSONRenderer

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory, TagFactory,
)
from lotus.serializers import (
    ArticleSerializer, ArticleMinimalSerializer, ArticleResumeSerializer,
)


# Shortcuts for shorter variable names
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
STATE_PREFIX = "article--"


@freeze_time("2012-10-15 10:00:00")
def test_article_articleserializer(db, settings, api_client):
    """
    Serializer 'ArticleSerializer' should returns the full payload as expected.
    """
    cover_uploadpath = settings.LOTUS_API_TEST_BASEURL + "/media/lotus/article/cover/"
    image_uploadpath = settings.LOTUS_API_TEST_BASEURL + "/media/lotus/article/image/"
    category_cover_uploadpath = (
        settings.LOTUS_API_TEST_BASEURL + "/media/lotus/category/cover/"
    )

    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object
    serialized = ArticleSerializer(None)
    assert serialized.data == {
        "tags": [],
        "language": None,
        "status": None,
        "featured": False,
        "pinned": False,
        "private": False,
        "publish_date": None,
        "publish_time": None,
        "publish_end": None,
        "last_update": None,
        "title": "",
        "slug": "",
        "seo_title": "",
        "lead": "",
        "introduction": "",
        "content": "",
        "cover": None,
        "image": None
    }

    # Date references
    utc = ZoneInfo("UTC")
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    ping = CategoryFactory(slug="ping")
    bingo = TagFactory(name="Bingo", slug="bingo")
    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")
    # This is not expected in result since different language should be filtered out
    pang = CategoryFactory(slug="pang", language="fr")

    original = ArticleFactory(
        title="Original",
        publish_date=now.date(),
        publish_time=now.time(),
    )

    related = ArticleFactory(
        title="Related",
        publish_date=now.date(),
        publish_time=now.time(),
        fill_categories=[ping],
        fill_tags=[bingo],
    )

    article = ArticleFactory(
        original=original,
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        featured=True,
        fill_categories=[ping, pang],
        fill_related=[related],
        fill_tags=[bingo],
        fill_authors=[picsou],
    )

    serialized = ArticleSerializer(article, context={
        "request": request,
        "lotus_now": now,
    })

    # print(json.dumps(serialized.data, indent=4))

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    payload = json.loads(JSONRenderer().render(serialized.data))

    assert payload == {
        "url": "http://testserver/api/article/3/",
        "detail_url": article.get_absolute_url(),
        "original": "http://testserver/api/article/1/",
        "tags": [
            "Bingo"
        ],
        "authors": [
            {
                "url": "http://testserver/api/author/1/",
                "detail_url": picsou.get_absolute_url(),
                "username": picsou.username,
                "first_name": picsou.first_name,
                "last_name": picsou.last_name,
            }
        ],
        "categories": [
            {
                "url": "http://testserver/api/category/1/",
                "detail_url": ping.get_absolute_url(),
                "language": ping.language,
                "title": ping.title,
                "lead": ping.lead,
                "description": ping.description,
                "cover": "http://testserver" + ping.cover.url,
            }
        ],
        "publish_datetime": "2012-10-16T10:00:00+00:00",
        "related": [
            {
                "detail_url": related.get_absolute_url(),
                "introduction": related.introduction,
                "language": related.language,
                "publish_datetime": "2012-10-15T10:00:00+00:00",
                "states": [
                    "available"
                ],
                "title": related.title,
                "url": "http://testserver/api/article/2/",
                "cover": "http://testserver" + related.cover.url,
            }
        ],
        "states": [
            "featured",
            "available",
            "not-yet",
        ],
        "language": article.language,
        "status": article.status,
        "featured": article.featured,
        "pinned": article.pinned,
        "private": article.private,
        "publish_date": "2012-10-16",
        "publish_time": "10:00:00",
        "publish_end": None,
        "last_update": "2012-10-15T12:00:00+02:00",
        "title": article.title,
        "slug": article.slug,
        "seo_title": "",
        "lead": article.lead,
        "introduction": article.introduction,
        "content": article.content,
        "cover": "http://testserver" + article.cover.url,
        "image": "http://testserver" + article.image.url,
    }


@freeze_time("2012-10-15 10:00:00")
def test_article_articleserializer_states(db, settings, api_client):
    """
    Serializer 'ArticleSerializer' payload should have the right states.
    """
    # Date references
    utc = ZoneInfo("UTC")
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # Without "lotus_now" argument for current date to check against, publish date
    # states are not present
    article = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )
    serialized = ArticleSerializer(article, context={
        "request": request,
    })
    assert serialized.data.get("states") == [
        "available",
    ]

    # When "lotus_now" argument is given, the right publish date states are there
    article = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )
    serialized = ArticleSerializer(article, context={
        "request": request,
        "lotus_now": now,
    })
    assert serialized.data.get("states") == [
        "available",
        "not-yet",
    ]

    # Some other variant of states with different Article parameters
    article = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        featured=True,
        status=STATUS_DRAFT,
    )
    serialized = ArticleSerializer(article, context={
        "request": request,
        "lotus_now": now,
    })
    assert serialized.data.get("states") == [
        "featured",
        "draft",
    ]


@freeze_time("2012-10-15 10:00:00")
def test_article_articleresumeserializer(db, settings, api_client):
    """
    Serializer 'ArticleResumeSerializer' should returns the resumed payload as expected.
    """
    cover_uploadpath = settings.LOTUS_API_TEST_BASEURL + "/media/lotus/article/cover/"

    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object
    serialized = ArticleResumeSerializer(None)
    assert serialized.data == {
        "cover": None,
        "introduction": "",
        "language": None,
        "seo_title": "",
        "slug": "",
        "tags": [],
        "title": ""
    }

    # Date references
    utc = ZoneInfo("UTC")
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    article = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )

    serialized = ArticleResumeSerializer(article, context={
        "request": request,
        "lotus_now": now,
    })

    payload = serialized.data
    assert payload == {
        "authors": [],
        "categories": [],
        "detail_url": article.get_absolute_url(),
        "introduction": article.introduction,
        "language": article.language,
        "publish_datetime": "2012-10-16T10:00:00+00:00",
        "seo_title": "",
        "slug": article.slug,
        "states": [
            "available",
            "not-yet",
        ],
        "tags": [],
        "title": article.title,
        "url": "http://testserver/api/article/1/",
        "cover": "http://testserver" + article.cover.url,
    }


@freeze_time("2012-10-15 10:00:00")
def test_article_articleminimalserializer(db, settings, api_client):
    """
    Serializer 'ArticleMinimalSerializer' should returns the very minimal payload as
    expected.
    """
    cover_uploadpath = settings.LOTUS_API_TEST_BASEURL + "/media/lotus/article/cover/"

    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object
    serialized = ArticleMinimalSerializer(None)
    assert serialized.data == {
        "cover": None,
        "introduction": "",
        "language": None,
        "title": ""
    }

    # Date references
    utc = ZoneInfo("UTC")
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    article = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        status=STATUS_DRAFT,
    )

    serialized = ArticleMinimalSerializer(article, context={"request": request})

    payload = serialized.data

    assert payload == {
        "detail_url": article.get_absolute_url(),
        "introduction": article.introduction,
        "language": article.language,
        "publish_datetime": "2012-10-16T10:00:00+00:00",
        "states": [
            "draft"
        ],
        "title": article.title,
        "url": "http://testserver/api/article/1/",
        "cover": "http://testserver" + article.cover.url,
    }
