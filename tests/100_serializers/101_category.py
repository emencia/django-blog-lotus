import datetime
import json

import pytest
from freezegun import freeze_time

from django.contrib.auth.models import AnonymousUser

try:
    from rest_framework.test import APIRequestFactory
    from rest_framework.renderers import JSONRenderer
    from lotus.serializers import (
        CategorySerializer, CategoryMinimalSerializer, CategoryResumeSerializer,
    )
    from lotus.viewsets.mixins import ArticleFilterAbstractViewset
except ModuleNotFoundError:
    APIRequestFactory, JSONRenderer = None, None
    API_AVAILABLE = False
else:
    API_AVAILABLE = True

from lotus.choices import get_category_template_default
from lotus.compat.import_zoneinfo import ZoneInfo
from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory, TagFactory,
)


pytestmark = pytest.mark.skipif(
    not API_AVAILABLE,
    reason="Django REST is not available, API is disabled"
)


@freeze_time("2012-10-15 10:00:00")
def test_category_categoryserializer(db, settings, api_client):
    """
    Serializer 'CategorySerializer' should returns the full payload as expected
    depending serializer has been given (from context) a filtering function or not.
    """
    settings.LANGUAGE_CODE = "en"

    # Build a dummy request, we don't care about requested URL.
    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object
    serialized = CategorySerializer(None)
    # print()
    # print(json.dumps(serialized.data, indent=4))
    # print()
    assert serialized.data == {
        "language": None,
        "title": "",
        "slug": "",
        "lead": "",
        "description": "",
        "cover": None,
        "depth": None,
        "cover_alt_text": "",
        "template": None,
    }

    # Timezone defined from project settings, used to format displayed date
    site_tz = ZoneInfo(settings.TIME_ZONE)
    # Date references
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=ZoneInfo("UTC"))

    pang = CategoryFactory(title="Pang", slug="pang")
    ping = CategoryFactory(title="Ping", slug="ping")
    pong = CategoryFactory(title="Pong", slug="pong")
    bim = CategoryFactory(title="Bim", slug="bim", language="fr", original=ping)
    # Make a tree of categories such as Pang > Ping > Pong
    # NOTE: Objects need to be reloaded in order since treebear may change the paths
    # that would lead to improper subpaths
    ping.move_into(pang)
    pang.refresh_from_db()
    ping.refresh_from_db()
    pong.move_into(ping)
    pong.refresh_from_db()

    bingo = TagFactory(name="Bingo", slug="bingo")
    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")

    now_article = ArticleFactory(
        title="Now",
        fill_authors=[picsou],
        publish_date=now.date(),
        publish_time=now.time(),
        fill_categories=[ping],
        fill_tags=[bingo],
    )

    tomorrow_article = ArticleFactory(
        title="Tomorrow",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        fill_categories=[ping],
        fill_tags=[bingo],
    )

    private_article = ArticleFactory(
        title="Private",
        publish_date=now.date(),
        publish_time=now.time(),
        private=True,
        fill_categories=[ping],
        fill_tags=[bingo],
    )

    serialized = CategorySerializer(ping, context={
        "request": request,
        "lotus_now": now,
    })
    # print(json.dumps(serialized.data, indent=4))

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    rendered = JSONRenderer().render(serialized.data)
    assert json.loads(rendered) == {
        "url": "http://testserver/api/category/{}/".format(ping.id),
        "original": None,
        "detail_url": ping.get_absolute_url(),
        "parent": {
            "url": "http://testserver/api/category/{}/".format(pang.id),
            "detail_url": pang.get_absolute_url(),
            "language": pang.language,
            "title": pang.title,
            "lead": pang.lead,
            "cover": "http://testserver" + pang.cover.url,
        },
        "articles": [
            {
                "detail_url": tomorrow_article.get_absolute_url(),
                "introduction": tomorrow_article.introduction,
                "language": tomorrow_article.language,
                "publish_datetime": "2012-10-16T10:00:00+00:00",
                "states": [
                    "available",
                    "not-yet"
                ],
                "title": tomorrow_article.title,
                "url": "http://testserver/api/article/{}/".format(tomorrow_article.id),
                "cover": "http://testserver" + tomorrow_article.cover.url,
            },
            {
                "detail_url": now_article.get_absolute_url(),
                "introduction": now_article.introduction,
                "language": now_article.language,
                "publish_datetime": "2012-10-15T10:00:00+00:00",
                "states": [
                    "available"
                ],
                "title": now_article.title,
                "url": "http://testserver/api/article/{}/".format(now_article.id),
                "cover": "http://testserver" + now_article.cover.url,
            },
            {
                "detail_url": private_article.get_absolute_url(),
                "introduction": private_article.introduction,
                "language": private_article.language,
                "publish_datetime": "2012-10-15T10:00:00+00:00",
                "states": [
                    "private",
                    "available"
                ],
                "title": private_article.title,
                "url": "http://testserver/api/article/{}/".format(private_article.id),
                "cover": "http://testserver" + private_article.cover.url,
            },
        ],
        "translations": [{
            "url": "http://testserver/api/category/{}/".format(bim.id),
            "detail_url": bim.get_absolute_url(),
            "language": bim.language,
            "title": bim.title,
            "lead": bim.lead,
            "cover": "http://testserver" + bim.cover.url,
        }],
        "children": [{
            "url": "http://testserver/api/category/{}/".format(pong.id),
            "detail_url": pong.get_absolute_url(),
            "language": pong.language,
            "title": pong.title,
            "lead": pong.lead,
            "cover": "http://testserver" + pong.cover.url,
        }],
        "language": ping.language,
        "title": ping.title,
        "slug": ping.slug,
        "lead": ping.lead,
        "modified": ping.modified.astimezone(site_tz).isoformat(),
        "cover": "http://testserver" + ping.cover.url,
        "cover_alt_text": ping.cover_alt_text,
        "description": ping.description,
        "depth": ping.depth,
        "template": get_category_template_default(),
    }

    # Craft a proper viewset class with a request and that can be used to give
    # a working filtering function
    filternator = ArticleFilterAbstractViewset()
    filternator.request = request
    filternator.request.user = AnonymousUser()

    # Enable filtering function
    filtered_and_serialized = CategorySerializer(ping, context={
        "request": request,
        "article_filter_func": filternator.apply_article_lookups,
        "lotus_now": now,
    })

    # print(json.dumps(filtered_and_serialized.data, indent=4))

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    rendered = JSONRenderer().render(filtered_and_serialized.data)
    assert json.loads(rendered) == {
        "url": "http://testserver/api/category/{}/".format(ping.id),
        "original": None,
        "detail_url": ping.get_absolute_url(),
        "parent": {
            "url": "http://testserver/api/category/{}/".format(pang.id),
            "detail_url": pang.get_absolute_url(),
            "language": pang.language,
            "title": pang.title,
            "lead": pang.lead,
            "cover": "http://testserver" + pang.cover.url,
        },
        "articles": [
            {
                "detail_url": now_article.get_absolute_url(),
                "introduction": now_article.introduction,
                "language": now_article.language,
                "publish_datetime": "2012-10-15T10:00:00+00:00",
                "states": [
                    "available"
                ],
                "title": now_article.title,
                "url": "http://testserver/api/article/{}/".format(now_article.id),
                "cover": "http://testserver" + now_article.cover.url,
            },
        ],
        "translations": [{
            "url": "http://testserver/api/category/{}/".format(bim.id),
            "detail_url": bim.get_absolute_url(),
            "language": bim.language,
            "title": bim.title,
            "lead": bim.lead,
            "cover": "http://testserver" + bim.cover.url,
        }],
        "children": [{
            "url": "http://testserver/api/category/{}/".format(pong.id),
            "detail_url": pong.get_absolute_url(),
            "language": pong.language,
            "title": pong.title,
            "lead": pong.lead,
            "cover": "http://testserver" + pong.cover.url,
        }],
        "language": ping.language,
        "title": ping.title,
        "slug": ping.slug,
        "lead": ping.lead,
        "modified": ping.modified.astimezone(site_tz).isoformat(),
        "cover": "http://testserver" + ping.cover.url,
        "cover_alt_text": ping.cover_alt_text,
        "description": ping.description,
        "depth": ping.depth,
        "template": get_category_template_default(),
    }


@freeze_time("2012-10-15 10:00:00")
def test_category_resume_serializer(db, api_client):
    """
    Serializer 'CategoryResumeSerializer' should returns the resumed payload as
    expected.
    """
    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object
    serialized = CategoryResumeSerializer(None)
    # print()
    # print(json.dumps(serialized.data, indent=4))
    # print()
    assert serialized.data == {
        "language": None,
        "title": "",
        "lead": "",
        "cover": None,
        "description": "",
    }

    # Date references
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))

    ping = CategoryFactory(slug="ping")

    serialized = CategoryResumeSerializer(ping, context={
        "request": request,
        "lotus_now": now,
    })

    # print(json.dumps(serialized.data, indent=4))

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    assert json.loads(JSONRenderer().render(serialized.data)) == {
        "url": "http://testserver/api/category/{}/".format(ping.id),
        "detail_url": ping.get_absolute_url(),
        "language": ping.language,
        "title": ping.title,
        "lead": ping.lead,
        "cover": "http://testserver" + ping.cover.url,
        "description": ping.description,
    }


@freeze_time("2012-10-15 10:00:00")
def test_category_minimal_serializer(db, api_client):
    """
    Serializer 'CategoryMinimalSerializer' should returns the resumed payload as
    expected.
    """
    request_factory = APIRequestFactory()
    request = request_factory.get("/")

    # A basic test with an empty object
    serialized = CategoryMinimalSerializer(None)
    # print()
    # print(json.dumps(serialized.data, indent=4))
    # print()
    assert serialized.data == {
        "language": None,
        "title": "",
        "lead": "",
        "cover": None,
    }

    # Date references
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=ZoneInfo("UTC"))

    ping = CategoryFactory(slug="ping")

    serialized = CategoryMinimalSerializer(ping, context={
        "request": request,
        "lotus_now": now,
    })

    # print(json.dumps(serialized.data, indent=4))

    # Use JSON render that will flatten data (turn OrderedDict as simple dict) to
    # ease assert and manipulation
    assert json.loads(JSONRenderer().render(serialized.data)) == {
        "url": "http://testserver/api/category/{}/".format(ping.id),
        "detail_url": ping.get_absolute_url(),
        "language": ping.language,
        "title": ping.title,
        "lead": ping.lead,
        "cover": "http://testserver" + ping.cover.url,
    }
