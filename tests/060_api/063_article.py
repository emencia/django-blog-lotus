import datetime
import json

import pytest
from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.conf import settings
from django.urls import reverse

from rest_framework.test import APIClient

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory, TagFactory,
)
from lotus.utils.tests import get_admin_change_url, html_pyquery


@freeze_time("2012-10-15 10:00:00")
def test_article_view_list_publication(db, client):
    """
    TODO
    """
    # Date references
    utc = ZoneInfo("UTC")
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)
    past_hour = datetime.datetime(2012, 10, 15, 9, 00).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    # Create 10 articles (according to pagination limit) with different publication
    # parameters
    # Numerate titles to enforce ordering since articles share the exact same datetimes
    # which would lead to arbitrary order from a session to another
    ArticleFactory(
        title="01. draft yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        status=STATUS_DRAFT,
    )
    ArticleFactory(
        title="02. published yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    ArticleFactory(
        title="03. published yesterday, ended one hour ago",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        publish_end=past_hour,
    )
    ArticleFactory(
        title="04. published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
    )
    ArticleFactory(
        title="05. pinned, published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        pinned=True,
    )
    ArticleFactory(
        title="06. featured, published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        featured=True,
    )
    ArticleFactory(
        title="07. private, published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        private=True,
    )
    ArticleFactory(
        title="08. published past hour, end next hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        publish_end=next_hour,
    )
    ArticleFactory(
        title="09. publish next hour",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    ArticleFactory(
        title="10. publish next hour, end tomorrow",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
        publish_end=tomorrow,
    )

    client = APIClient()
    url = reverse("lotus:api-article-list")
    print("url:", url)

    response = client.get(url)
    json_data = response.json()
    print()
    print(json.dumps(json_data, indent=4))

    assert response.status_code == 200

    assert 1 == 42
