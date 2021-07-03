import datetime

import pytest
from freezegun import freeze_time

from django.urls import reverse
from django.utils import timezone

from lotus.factories import ArticleFactory, AuthorFactory, CategoryFactory
from lotus.choices import STATUS_DRAFT

from lotus.utils.tests import html_pyquery


def test_article_view_detail_published(db, admin_client, client):
    """
    Published article is reachable from anyone.
    """
    instance = ArticleFactory()

    response = client.get(instance.get_absolute_url())
    assert response.status_code == 200

    response = admin_client.get(instance.get_absolute_url())
    assert response.status_code == 200


def test_article_view_detail_draft(db, admin_client, client):
    """
    Draft article is only reachable for admin in 'admin mode'.
    """
    user = AuthorFactory()
    instance = ArticleFactory(status=STATUS_DRAFT)

    # With default behavior a draft is not available no matter it's for an admin or not
    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    response = admin_client.get(instance.get_absolute_url())
    assert response.status_code == 404

    # Admin mode behavior do not work for non admin users
    response = client.get(instance.get_absolute_url(), {"admin": 1})
    assert response.status_code == 404

    client.force_login(user)
    response = client.get(instance.get_absolute_url(), {"admin": 1})
    assert response.status_code == 404

    # Admin mode behavior only work for admin users
    response = admin_client.get(instance.get_absolute_url(), {"admin": 1})
    assert response.status_code == 200


def test_article_view_detail_private(db, client):
    """
    Private article is reachable only for authenticated users.
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

    response = admin_client.get(instance.get_absolute_url(), {"admin": 1})
    assert response.status_code == 200


@freeze_time("2010-10-15")
@pytest.mark.parametrize("user_kind,client_kwargs,expected", [
    (
        "anonymous",
        {},
        [
            # Expected title and CSS classes
            ["05. pinned, published past hour", ["pinned"]],
            ["09. publish next hour", []],
            ["10. publish next hour, end tomorrow", []],
            ["04. published past hour", []],
            ["06. featured, published past hour", ["featured"]],
            ["08. published past hour, end next hour", []],
            ["02. published yesterday", []],
        ],
    ),
    (
        "anonymous",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["05. pinned, published past hour", ["pinned"]],
            ["09. publish next hour", []],
            ["10. publish next hour, end tomorrow", []],
            ["04. published past hour", []],
            ["06. featured, published past hour", ["featured"]],
            ["08. published past hour, end next hour", []],
            ["02. published yesterday", []],
        ],
    ),
    (
        "user",
        {},
        [
            # Expected title and CSS classes
            ["05. pinned, published past hour", ["pinned"]],
            ["09. publish next hour", []],
            ["10. publish next hour, end tomorrow", []],
            ["04. published past hour", []],
            ["06. featured, published past hour", ["featured"]],
            ["07. private, published past hour", []],
            ["08. published past hour, end next hour", []],
            ["02. published yesterday", []],
        ],
    ),
    (
        "user",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["05. pinned, published past hour", ["pinned"]],
            ["09. publish next hour", []],
            ["10. publish next hour, end tomorrow", []],
            ["04. published past hour", []],
            ["06. featured, published past hour", ["featured"]],
            ["07. private, published past hour", []],
            ["08. published past hour, end next hour", []],
            ["02. published yesterday", []],
        ],
    ),
    (
        "admin",
        {},
        [
            # Expected title and CSS classes
            ["05. pinned, published past hour", ["pinned"]],
            ["09. publish next hour", []],
            ["10. publish next hour, end tomorrow", []],
            ["04. published past hour", []],
            ["06. featured, published past hour", ["featured"]],
            ["07. private, published past hour", []],
            ["08. published past hour, end next hour", []],
            ["02. published yesterday", []],
        ],
    ),
    (
        "admin",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["05. pinned, published past hour", ["pinned"]],
            ["09. publish next hour", []],
            ["10. publish next hour, end tomorrow", []],
            ["04. published past hour", []],
            ["06. featured, published past hour", ["featured"]],
            ["07. private, published past hour", []],
            ["08. published past hour, end next hour", []],
            ["01. draft yesterday", ["draft"]],
            ["02. published yesterday", []],
            ["03. published yesterday, ended one hour ago", []],
        ],
    ),
])
def test_article_view_list_publication(db, admin_client, client, user_kind,
                                       client_kwargs, expected):
    """
    View list should respect publication criterias (dates and state, private article and
    order.

    Tested again profiles:

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

    # Select the right client to use for user kind
    enabled_client = client_for[user_kind]
    # We have to force authenticated user (non admin)
    if user_kind == "user":
        user = AuthorFactory()
        client.force_login(user)

    # Get all available items from HTML page
    urlname = "lotus:article-index"
    response = enabled_client.get(reverse(urlname), client_kwargs)
    assert response.status_code == 200

    # Parse HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .article-list-container .list .item")

    # Get useful content from list items
    content = []
    for item in items:
        title = item.cssselect("h3 > a")[0].text
        # Drop item class since it's useless for test
        classes = [v for v in item.get("class").split() if v != "item"]
        content.append([title, classes])

    assert content == expected


def test_article_view_detail_content(db, admin_client):
    """
    Detail view should contain all expected content and relations.

    Note we are requesting with admin mode to be able to see a draft
    article to check for the "draft" CSS class.

    Also, this does not care about textual content (title, lead, content, etc..).
    """
    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")
    AuthorFactory(first_name="Flairsou", last_name="Cresus")

    cat_1 = CategoryFactory(title="cat_1")
    CategoryFactory(title="cat_2")
    CategoryFactory(title="cat_3")

    ArticleFactory(title="Foo")
    article_2 = ArticleFactory(title="Bar")
    article_3 = ArticleFactory(
        title="Ping",
        fill_categories=[cat_1],
        fill_related=[article_2],
        fill_authors=[picsou],
        status=STATUS_DRAFT,
        pinned=True,
        featured=True,
        private=True,
    )

    # Get detail HTML page
    response = admin_client.get(article_3.get_absolute_url(), {"admin": 1})
    assert response.status_code == 200

    # Parse HTML response to get content and relations
    dom = html_pyquery(response)
    container = dom.find("#lotus-content .article-detail")[0]
    categories = [item.text for item in dom.find("#lotus-content .categories li a")]
    authors = [item.text for item in dom.find("#lotus-content .authors li")]
    relateds = [item.text for item in dom.find("#lotus-content .relateds li a")]
    cover = dom.find("#lotus-content .cover img")[0].get("src")
    large_img = dom.find("#lotus-content .image img")[0].get("src")
    classes = sorted([
        v for v in container.get("class").split()
        if v != "article-detail"
    ])

    assert categories == ["cat_1"]
    assert authors == ["Picsou McDuck"]
    assert relateds == ["Bar"]
    assert classes == ["draft", "featured", "pinned", "private"]
    assert cover == article_3.cover.url
    assert large_img == article_3.image.url
