import datetime
import json

import pytest
from freezegun import freeze_time

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

try:
    from rest_framework.test import APIRequestFactory
    from rest_framework.renderers import JSONRenderer
    from lotus.serializers import (
        ArticleSerializer, ArticleMinimalSerializer, ArticleResumeSerializer,
    )
    from lotus.viewsets.mixins import ArticleFilterAbstractViewset
except ModuleNotFoundError:
    APIRequestFactory, JSONRenderer = None, None
    API_AVAILABLE = False
else:
    API_AVAILABLE = True

from lotus.choices import STATUS_DRAFT
from lotus.compat.import_zoneinfo import ZoneInfo
from lotus.factories import (
    AlbumFactory, AlbumItemFactory, ArticleFactory, AuthorFactory, CategoryFactory,
    TagFactory,
)


pytestmark = pytest.mark.skipif(
    not API_AVAILABLE,
    reason="Django REST is not available, API is disabled"
)


# Shortcuts for shorter variable names
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
STATE_PREFIX = "article--"


@freeze_time("2012-10-15 10:00:00")
def test_article_articleserializer(db, api_client):
    """
    Serializer 'ArticleSerializer' should returns the full payload as expected.
    """
    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object won't have any relation field
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
        "cover_alt_text": "",
        "image": None,
        "image_alt_text": "",
    }

    # Date references
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=ZoneInfo("UTC"))

    ping = CategoryFactory(slug="ping")
    bingo = TagFactory(name="Bingo", slug="bingo")
    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")
    album = AlbumFactory(title="foo")
    albumitem_1 = AlbumItemFactory(album=album)
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
        album=album,
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
    assert json.loads(JSONRenderer().render(serialized.data)) == {
        "url": "http://testserver/api/article/{}/".format(article.id),
        "detail_url": article.get_absolute_url(),
        "original": "http://testserver/api/article/{}/".format(original.id),
        "tags": [
            "Bingo"
        ],
        "authors": [
            {
                "url": "http://testserver/api/author/{}/".format(picsou.id),
                "detail_url": picsou.get_absolute_url(),
                "first_name": picsou.first_name,
                "last_name": picsou.last_name,
            }
        ],
        "categories": [
            {
                "url": "http://testserver/api/category/{}/".format(ping.id),
                "detail_url": ping.get_absolute_url(),
                "language": ping.language,
                "title": ping.title,
                "lead": ping.lead,
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
                "url": "http://testserver/api/article/{}/".format(related.id),
                "cover": "http://testserver" + related.cover.url,
            }
        ],
        "states": [
            "featured",
            "available",
            "not-yet",
        ],
        "translations": [],
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
        "cover_alt_text": article.cover_alt_text,
        "image": "http://testserver" + article.image.url,
        "image_alt_text": article.image_alt_text,
        "album": {
            "items": [
                {
                    "modified": "2012-10-15T12:00:00+02:00",
                    "title": albumitem_1.title,
                    "order": albumitem_1.order,
                    "media": "http://testserver" + albumitem_1.media.url,
                },
            ],
            "modified": "2012-10-15T12:00:00+02:00",
            "title": album.title,
        },
    }


@freeze_time("2012-10-15 10:00:00")
def test_article_articleserializer_states(db, api_client):
    """
    Serializer 'ArticleSerializer' payload should have the right states.
    """
    # Date references
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=ZoneInfo("UTC"))

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
def test_article_articleresumeserializer(db, api_client):
    """
    Serializer 'ArticleResumeSerializer' should returns the resumed payload as expected.
    """
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
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=ZoneInfo("UTC"))

    main = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )

    serialized = ArticleResumeSerializer(main, context={
        "request": request,
        "lotus_now": now,
    })

    payload = serialized.data
    assert payload == {
        "authors": [],
        "categories": [],
        "detail_url": main.get_absolute_url(),
        "introduction": main.introduction,
        "language": main.language,
        "publish_datetime": "2012-10-16T10:00:00+00:00",
        "seo_title": "",
        "slug": main.slug,
        "states": [
            "available",
            "not-yet",
        ],
        "tags": [],
        "title": main.title,
        "url": "http://testserver/api/article/1/",
        "cover": "http://testserver" + main.cover.url,
    }


@freeze_time("2012-10-15 10:00:00")
def test_article_articleminimalserializer(db, api_client):
    """
    Serializer 'ArticleMinimalSerializer' should returns the very minimal payload as
    expected.
    """
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
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=ZoneInfo("UTC"))

    main = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        status=STATUS_DRAFT,
    )

    serialized = ArticleMinimalSerializer(main, context={"request": request})

    payload = serialized.data

    assert payload == {
        "detail_url": main.get_absolute_url(),
        "introduction": main.introduction,
        "language": main.language,
        "publish_datetime": "2012-10-16T10:00:00+00:00",
        "states": [
            "draft"
        ],
        "title": main.title,
        "url": "http://testserver/api/article/1/",
        "cover": "http://testserver" + main.cover.url,
    }


@freeze_time("2012-10-15 10:00:00")
def test_article_articleserializer_get_related(db, api_client):
    """
    Related articles from payload should be properly filtered depending serializer has
    a filtering function or not.
    """
    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # Date references
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=ZoneInfo("UTC"))
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=ZoneInfo("UTC"))
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=ZoneInfo("UTC"))

    draft = ArticleFactory(
        title="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    published_yesterday = ArticleFactory(
        title="published yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    published_notyet = ArticleFactory(
        title="not yet published",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )
    french = ArticleFactory(
        title="french",
        publish_date=today.date(),
        publish_time=today.time(),
        language="fr",
    )

    main = ArticleFactory(
        title="Lorem ipsum",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_related=[draft, published_yesterday, published_notyet, french],
    )

    # Without filtering function, only language is filtered
    serialized = ArticleSerializer(main, context={
        "request": request,
        "lotus_now": now,
    })

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    results = sorted([
        item["title"]
        for item in json.loads(json.dumps(serialized.data["related"]))
    ])
    assert results == [
        "draft",
        "not yet published",
        "published yesterday",
    ]

    # Craft a proper viewset class with a request and that can be used to give
    # a working filtering function
    filternator = ArticleFilterAbstractViewset()
    filternator.request = request
    filternator.request.user = AnonymousUser()

    # With a given filtering function
    serialized = ArticleSerializer(main, context={
        "request": request,
        "lotus_now": now,
        "article_filter_func": filternator.apply_article_lookups,
    })

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    results = sorted([
        item["title"]
        for item in json.loads(json.dumps(serialized.data["related"]))
    ])
    assert results == ["published yesterday"]


@freeze_time("2012-10-15 10:00:00")
def test_article_articleserializer_get_translations(db, api_client, settings):
    """
    Translation articles from payload should be properly filtered depending serializer
    has a filtering function or not.
    """
    settings.LANGUAGE_CODE = "en"

    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # Date references
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=ZoneInfo("UTC"))

    main = ArticleFactory(
        title="Lorem ipsum",
        publish_date=today.date(),
        publish_time=today.time(),
    )
    ArticleFactory(
        title="french",
        publish_date=today.date(),
        publish_time=today.time(),
        language="fr",
        original=main,
    )
    ArticleFactory(
        title="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        language="de",
        status=STATUS_DRAFT,
        original=main,
    )

    # Without filtering function, only language is filtered
    serialized = ArticleSerializer(main, context={
        "request": request,
        "lotus_now": now,
    })

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    results = sorted([
        item["title"]
        for item in json.loads(json.dumps(serialized.data["translations"]))
    ])
    assert results == ["draft", "french"]

    # Craft a proper viewset class with a request and that can be used to give
    # a working filtering function
    filternator = ArticleFilterAbstractViewset()
    filternator.request = request
    filternator.request.user = AnonymousUser()

    # With a given filtering function
    serialized = ArticleSerializer(main, context={
        "request": request,
        "lotus_now": now,
        "article_filter_func": filternator.apply_article_lookups,
    })

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    results = sorted([
        item["title"]
        for item in json.loads(json.dumps(serialized.data["translations"]))
    ])
    assert results == ["french"]
