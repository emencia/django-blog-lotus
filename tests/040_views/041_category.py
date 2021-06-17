import datetime

import pytest

from django.urls import reverse
from django.utils import timezone

from lotus.factories import ArticleFactory, AuthorFactory, CategoryFactory
from lotus.choices import STATUS_DRAFT

from lotus.utils.tests import html_pyquery


def test_article_view_detail_404(db, client):
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


def test_article_view_detail_success(db, client):
    """
    Category detail page should have category contents and related articles.

    TODO:
        Related articles.
    """
    picsou_category = CategoryFactory(
        title="Picsou",
        slug="picsou",
    )

    response = client.get(picsou_category.get_absolute_url())
    assert response.status_code == 200

    # Parse HTML
    dom = html_pyquery(response)
    title = dom.find("#lotus-content .category-detail h2")[0].text
    cover = dom.find("#lotus-content .cover img")[0].get("src")

    assert title == picsou_category.title
    assert cover == picsou_category.cover.url

    assert 1 == 42


@pytest.mark.skip(reason="To do when detail has been covered")
def test_article_view_list(db, admin_client, client):
    """
    TODO
    """
    assert "TODO" == "NOT YET"
