import datetime

import pytest

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from lotus.factories import ArticleFactory, AuthorFactory, CategoryFactory
from lotus.choices import STATUS_DRAFT

from lotus.utils.tests import html_pyquery


def test_category_view_detail_404(db, client):
    """
    Trying to get unexisting Category should return a 404 response.
    """
    # Create a dummy object to get correct URL then delete it
    flairsou_category = CategoryFactory(
        title="Picsou",
        slug="picsou",
    )
    url = flairsou_category.get_absolute_url()
    flairsou_category.delete()

    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize("user_kind,client_kwargs,expected", [
    (
        "anonymous",
        {},
        [
            # Expected title and CSS classes
            ["Pinned", ["pinned"]],
            ["Featured", ["featured"]],
            ["06. Plip", []],
            ["05. Plop", []],
            ["04. Pong", []],
            ["03. Ping", []],
            ["02. Bar", []],
            ["01. Foo", []],
        ],
    ),
    (
        "anonymous",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["Pinned", ["pinned"]],
            ["Featured", ["featured"]],
            ["06. Plip", []],
            ["05. Plop", []],
            ["04. Pong", []],
            ["03. Ping", []],
            ["02. Bar", []],
            ["01. Foo", []],
        ],
    ),
    (
        "user",
        {},
        [
            # Expected title and CSS classes
            ["Pinned", ["pinned"]],
            ["Featured", ["featured"]],
            ["06. Plip", []],
            ["05. Plop", []],
            ["04. Pong", []],
            ["03. Ping", []],
            ["02. Bar", []],
            ["01. Foo", []],
            ["Private", []],
        ],
    ),
    (
        "user",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["Pinned", ["pinned"]],
            ["Featured", ["featured"]],
            ["06. Plip", []],
            ["05. Plop", []],
            ["04. Pong", []],
            ["03. Ping", []],
            ["02. Bar", []],
            ["01. Foo", []],
            ["Private", []],
        ],
    ),
    (
        "admin",
        {},
        [
            # Expected title and CSS classes
            ["Pinned", ["pinned"]],
            ["Featured", ["featured"]],
            ["06. Plip", []],
            ["05. Plop", []],
            ["04. Pong", []],
            ["03. Ping", []],
            ["02. Bar", []],
            ["01. Foo", []],
            ["Private", []],
        ],
    ),
    (
        "admin",
        {"admin": 1},
        [
            # Expected title and CSS classes
            ["Pinned", ["pinned"]],
            ["Featured", ["featured"]],
            ["06. Plip", []],
            ["05. Plop", []],
            ["04. Pong", []],
            ["03. Ping", []],
            ["02. Bar", []],
            ["01. Foo", []],
            ["Private", []],
            ["In draft", ["draft"]],
        ],
    ),
])
def test_category_view_detail_content(db, admin_client, client, user_kind,
                                      client_kwargs, expected):
    """
    Category detail page should have category contents and related articles following
    publication rules (as described in article list view tests).
    """
    # Available Django clients as a dict to be able to switch on
    client_for = {
        "anonymous": client,
        "user": client,
        "admin": admin_client,
    }

    # Our main category to test
    picsou = CategoryFactory(title="Picsou", slug="picsou")

    # Should never display for this category
    ArticleFactory(title="Nope")
    ArticleFactory(title="Baguette", language="fr", fill_categories=[picsou])
    ArticleFactory(title="In draft", fill_categories=[picsou], status=STATUS_DRAFT)
    ArticleFactory(title="Private", fill_categories=[picsou], private=True)

    # A batch of articles with distinct name (since automatic name from factory is not
    # consistent enough)
    names = [
        "01. Foo", "02. Bar", "03. Ping", "04. Pong", "05. Plop", "06. Plip",
    ]
    for item in names:
        ArticleFactory(title=item, fill_categories=[picsou])

    # Use option to push these ones at top order
    ArticleFactory(title="Pinned", fill_categories=[picsou], pinned=True)
    ArticleFactory(title="Featured", fill_categories=[picsou], featured=True)

    # Select the right client to use for user kind
    enabled_client = client_for[user_kind]
    # We have to force authenticated user (non admin)
    if user_kind == "user":
        user = AuthorFactory()
        client.force_login(user)

    # Get detail page
    url = picsou.get_absolute_url()
    response = enabled_client.get(url, client_kwargs)
    assert response.status_code == 200

    # Parse HTML
    dom = html_pyquery(response)
    title = dom.find("#lotus-content .category-detail h2")[0].text
    cover = dom.find("#lotus-content .cover img")[0].get("src")

    assert title == picsou.title
    assert cover == picsou.cover.url

    # Get articles
    items = dom.find("#lotus-content .category-detail .articles .item")

    # Get useful content from list items
    content = []
    for item in items:
        title = item.cssselect("h3 > a")[0].text
        # Drop item class since it's useless for test
        classes = [v for v in item.get("class").split() if v != "item"]
        content.append([title, classes])

    assert content == expected


def test_category_view_detail_pagination(db, client):
    """
    Category detail should paginate its article list
    """
    # Our main category to test
    picsou = CategoryFactory(title="Picsou", slug="picsou")

    # No more articles than pagination limit
    articles = ArticleFactory.create_batch(
        settings.LOTUS_ARTICLE_PAGINATION,
        fill_categories=[picsou],
    )

    # Get detail page
    url = picsou.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200

    # Parse HTML
    dom = html_pyquery(response)
    pagination = dom.find("#lotus-content .category-detail .articles .pagination")
    #pagination = dom.find("#lotus-content .category-detail .articles .pagination a")

    # No pagination HTML is displayed when limit have not been reached
    assert len(pagination) == 0

    # Additional article to activate pagination
    ArticleFactory(fill_categories=[picsou])

    # With pagination activated there is at least two pages
    url = picsou.get_absolute_url()
    response = client.get(url)
    dom = html_pyquery(response)
    links = dom.find("#lotus-content .category-detail .articles .pagination a")
    assert len(links) == 2

    # Ensure the second page only have the remaining item
    page_2_arg = links[1].get("href")
    url = picsou.get_absolute_url() + page_2_arg
    response = client.get(url)
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .category-detail .articles .item")
    assert len(items) == 1


@pytest.mark.skip(reason="To do when detail has been covered")
def test_category_view_list(db, admin_client, client):
    """
    TODO
    """
    assert "TODO" == "NOT YET"
