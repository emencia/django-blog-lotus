import datetime
import os

import pytest

from django.urls import reverse
from django.utils import timezone

from lotus.factories import ArticleFactory, AuthorFactory, CategoryFactory
from lotus.choices import STATUS_DRAFT, STATUS_PUBLISHED

from lotus.utils.tests import html_pyquery


def test_article_view_detail_published(db, admin_client, client):
    """
    Published article are reachable from anyone.
    """
    instance = ArticleFactory()

    response = client.get(instance.get_absolute_url())
    assert response.status_code == 200

    response = admin_client.get(instance.get_absolute_url())
    assert response.status_code == 200


def test_article_view_detail_draft(db, admin_client, client):
    """
    Draft article are only reachable for admin in 'admin mode'.
    """
    user = AuthorFactory()
    instance = ArticleFactory(status=STATUS_DRAFT)

    # With default behavior a draft is not available not matter it's for an admin or
    # not
    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    response = admin_client.get(instance.get_absolute_url())
    assert response.status_code == 404

    # Admin mode behavior do not work for non admin users
    response = client.get(instance.get_absolute_url(), {'admin': 1})
    assert response.status_code == 404

    client.force_login(user)
    response = client.get(instance.get_absolute_url(), {'admin': 1})
    assert response.status_code == 404

    # Admin mode behavior only work for admin users
    response = admin_client.get(instance.get_absolute_url(), {'admin': 1})
    assert response.status_code == 200


def test_article_view_detail_private(db, client):
    """
    Private article are reachable only for authenticated users.
    """
    user = AuthorFactory()
    instance = ArticleFactory(private=True)

    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    client.force_login(user)
    response = client.get(instance.get_absolute_url())
    assert response.status_code == 200


def test_article_view_detail_publication(db, admin_client, client):
    """
    Publication criteria should be respected to view an Article, excepted for admin
    mode.
    """
    now = timezone.now()
    past_hour = now - datetime.timedelta(hours=1)

    instance = ArticleFactory(publish_end=past_hour)

    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    response = admin_client.get(instance.get_absolute_url(), {'admin': 1})
    assert response.status_code == 200


@pytest.mark.parametrize("user_kind,client_kwargs,expected", [
    (
        "anonymous",
        {},
        [
            # Expected title and CSS classes
            ["pinned, published past hour", ["pinned"]],
            ["published yesterday", []],
            ["published past hour", []],
            ["featured, published past hour", ["featured"]],
            ["published past hour, end next hour", []],
            ["publish next hour", []],
            ["publish next hour, end tomorrow", []]
        ],
    ),
    (
        "anonymous",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["pinned, published past hour", ["pinned"]],
            ["published yesterday", []],
            ["published past hour", []],
            ["featured, published past hour", ["featured"]],
            ["published past hour, end next hour", []],
            ["publish next hour", []],
            ["publish next hour, end tomorrow", []]
        ],
    ),
    (
        "admin",
        {},
        [
            # Expected title and CSS classes
            ["pinned, published past hour", ["pinned"]],
            ["published yesterday", []],
            ["published past hour", []],
            ["featured, published past hour", ["featured"]],
            ["private, published past hour", []],
            ["published past hour, end next hour", []],
            ["publish next hour", []],
            ["publish next hour, end tomorrow", []]
        ],
    ),
    (
        "admin",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["pinned, published past hour", ["pinned"]],
            ["draft yesterday", ["draft"]],
            ["published yesterday", []],
            ["published yesterday, ended one hour ago", []],
            ["published past hour", []],
            ["featured, published past hour", ["featured"]],
            ["private, published past hour", []],
            ["published past hour, end next hour", []],
            ["publish next hour", []],
            ["publish next hour, end tomorrow", []]
        ],
    ),
    (
        "user",
        {},
        [
            # Expected title and CSS classes
            ["pinned, published past hour", ["pinned"]],
            ["published yesterday", []],
            ["published past hour", []],
            ["featured, published past hour", ["featured"]],
            ["private, published past hour", []],
            ["published past hour, end next hour", []],
            ["publish next hour", []],
            ["publish next hour, end tomorrow", []]
        ],
    ),
    (
        "user",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["pinned, published past hour", ["pinned"]],
            ["published yesterday", []],
            ["published past hour", []],
            ["featured, published past hour", ["featured"]],
            ["private, published past hour", []],
            ["published past hour, end next hour", []],
            ["publish next hour", []],
            ["publish next hour, end tomorrow", []]
        ],
    ),
])
def test_article_view_list_publication(db, admin_client, client, user_kind,
                                       client_kwargs, expected):
    """
    Publication criteria and privacy should be respected to list Articles, excepted for
    admin mode. Also order should be respected.

    TODO:
        Should be tested again:

        * non authenticated;
        * non authenticated trying to user admin mode;
        * authenticated user lambda;
        * authenticated user lambda trying to user admin mode;
        * admin without admin mode;
        * admin with admin mode;
    """
    # Available Django clients as a dict to be able to switch on
    client_for = {
        "anonymous": client,
        "user": client,
        "admin": admin_client,
    }

    # Date references
    now = timezone.now()
    yesterday = now - datetime.timedelta(days=1)
    past_hour = now - datetime.timedelta(hours=1)
    tomorrow = now + datetime.timedelta(days=1)
    next_hour = now + datetime.timedelta(hours=1)

    # Create 10 articles (according to pagination limit) with different publication
    # parameters
    ArticleFactory(
        title="draft yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        status=STATUS_DRAFT,
    )
    ArticleFactory(
        title="published yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    ArticleFactory(
        title="published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
    )
    ArticleFactory(
        title="pinned, published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        pinned=True,
    )
    ArticleFactory(
        title="featured, published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        featured=True,
    )
    ArticleFactory(
        title="private, published past hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        private=True,
    )
    ArticleFactory(
        title="published yesterday, ended one hour ago",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        publish_end=past_hour,
    )
    ArticleFactory(
        title="published past hour, end next hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time(),
        publish_end=next_hour,
    )
    ArticleFactory(
        title="publish next hour",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    ArticleFactory(
        title="publish next hour, end tomorrow",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
        publish_end=tomorrow,
    )

    # Select the right client to use for user kind
    enabled_client = client_for[user_kind]
    # We have to force authenticated user (non admin)
    if user_kind == "user":
        user = AuthorFactory()
        client.force_login(user)

    urlname = "lotus:article-index"
    response = enabled_client.get(reverse(urlname), client_kwargs)

    dom = html_pyquery(response)
    items = dom.find("#lotus-content .article-list-container .list .item")

    # Get useful content from list items
    content = []
    for item in items:
        title = item.cssselect("h3 > a")[0].text
        # Drop item class since it's useless for test
        classes = [v for v in item.get("class").split() if v != "item"]
        content.append([title, classes])

    import json
    print(json.dumps(content, indent=4))

    assert content == expected
