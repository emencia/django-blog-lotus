import datetime
import json
from pathlib import Path

import pytest
from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APIRequestFactory

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
def test_article_articleserializer_empty(db, settings, api_client):
    """
    TODO:
    Serializer 'ArticleSerializer' should returns the full payload as expected.
    """
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


@freeze_time("2012-10-15 10:00:00")
def test_article_articleserializer_base(db, settings, api_client):
    """
    TODO:
    Serializer 'ArticleSerializer' should returns the full payload as expected.
    """
    cover_path = settings.LOTUS_API_TEST_BASEURL + "/media/lotus/article/cover/"
    # Date references
    utc = ZoneInfo("UTC")
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    article = ArticleFactory(
        title="Lorem ipsum",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        status=STATUS_DRAFT,
    )

    request_factory = APIRequestFactory()
    request = request_factory.get("/")
    serialized = ArticleSerializer(article, context={"request": request})

    import json
    print(json.dumps(serialized.data, indent=4))

    payload = serialized.data
    cover = payload.pop("cover")
    image = payload.pop("image")

    assert payload == {
        "url": "http://testserver/en/api/article/1/",
        "detail_url": article.get_absolute_url(),
        "original": None,
        "tags": [],
        "authors": [],
        "categories": [],
        "publish_datetime": "2012-10-16T10:00:00+00:00",
        "related": [],
        "states": [
            "draft"
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
        #"cover": "http://testserver/media/lotus/article/cover/12/10/5575ac83-0b42-49c5-8829-37f8173fa5af.png",
        #"image": "http://testserver/media/lotus/article/image/12/10/9a8b59ea-d79e-4203-a1ec-29fb3ab46668.png"
    }

    assert cover.startswith(cover_path) is True

    assert 1 == 42
