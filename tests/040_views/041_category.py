import datetime

import pytest

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


def test_category_view_detail_success(db, client):
    """
    Category detail page should have category contents and related articles.

    TODO:
        Related articles.
    """
    category_picsou = CategoryFactory(
        title="Picsou",
        slug="picsou",
    )

    ArticleFactory(title="Nope")
    article_foo = ArticleFactory(
        title="Foo",
        fill_categories=[category_picsou],
    )
    article_bar = ArticleFactory(
        title="Bar",
        fill_categories=[category_picsou],
        status=STATUS_DRAFT,
        pinned=True,
        featured=True,
        private=True,
    )

    response = client.get(category_picsou.get_absolute_url())
    assert response.status_code == 200

    # Parse HTML
    dom = html_pyquery(response)
    title = dom.find("#lotus-content .category-detail h2")[0].text
    cover = dom.find("#lotus-content .cover img")[0].get("src")

    assert title == category_picsou.title
    assert cover == category_picsou.cover.url

    # Get articles
    items = dom.find("#lotus-content .category-detail .articles .item")

    # Get useful content from list items
    content = []
    for item in items:
        title = item.cssselect("h3 > a")[0].text
        # Drop item class since it's useless for test
        classes = [v for v in item.get("class").split() if v != "item"]
        content.append([title, classes])

    assert content == [
        ["Bar", ["pinned", "featured", "draft"]],
        ["Foo", []]
    ]

    assert 1 == 42


@pytest.mark.skip(reason="To do when detail has been covered")
def test_category_view_list(db, admin_client, client):
    """
    TODO
    """
    assert "TODO" == "NOT YET"
