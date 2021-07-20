import pytest

from django.conf import settings
from django.urls import reverse

from lotus.factories import ArticleFactory, AuthorFactory, CategoryFactory
from lotus.choices import STATUS_DRAFT

from lotus.utils.tests import html_pyquery


# Shortcut for a shorter variable name
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES


def test_author_view_detail_404(db, client):
    """
    Trying to get unexisting Author should return a 404 response.
    """
    # Create a dummy object to get correct URL then delete it
    dummy = AuthorFactory()
    url = dummy.get_absolute_url()
    dummy.delete()

    response = client.get(url)
    assert response.status_code == 404


def test_author_view_list(db, client):
    """
    Author list should be correctly ordered and paginated.
    """
    expected_pages = 2
    total_items = settings.LOTUS_AUTHOR_PAGINATION * expected_pages

    # Create a batch of author with numerated name on two digit filled with
    # leading 0 to enforce sorting
    authors = []
    names = [
        "{}_Foo".format(str(i).zfill(2))
        for i in range(1, total_items + 1)
    ]
    for item in names:
        authors.append(AuthorFactory(username=item))

    # A published article is required
    article = ArticleFactory(title="Sample", fill_authors=authors)

    # Additional author which are invisible because it does not have any published
    # article
    nietman = AuthorFactory(username="niet")
    ArticleFactory(title="Nope", fill_authors=[nietman])


    # Expected items in page are simply ordered on name
    expected_item_page_1 = names[0:settings.LOTUS_AUTHOR_PAGINATION]
    expected_item_page_2 = names[settings.LOTUS_AUTHOR_PAGINATION:total_items]

    # Get detail for first page
    urlname = "lotus:author-index"
    response = client.get(reverse(urlname))
    assert response.status_code == 200

    # Parse first page HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .author-list-container .list .author")
    print()
    print(dom.find("#lotus-content .author-list-container"))
    print()
    links = dom.find("#lotus-content .author-list-container .pagination a")
    # Get item titles
    link_title_page_1 = []
    for item in items:
        link_title_page_1.append(item.cssselect(".title")[0].text)

    # Expected pagination links
    assert len(links) == 2
    # Expected paginated item list length
    assert len(items) == settings.LOTUS_AUTHOR_PAGINATION
    # Ensure every expected items are here respecting order
    assert expected_item_page_1 == link_title_page_1

    # Get detail for second page
    urlname = "lotus:author-index"
    response = client.get(reverse(urlname), {"page": 2})
    assert response.status_code == 200

    # Parse second page HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .author-list-container .list .author")
    # Get item titles
    link_title_page_2 = []
    for item in items:
        link_title_page_2.append(item.cssselect(".title")[0].text)

    # Ensure every expected items are here respecting order
    assert expected_item_page_2 == link_title_page_2
