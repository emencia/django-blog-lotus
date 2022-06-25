import datetime

import pytest
import pytz
from freezegun import freeze_time

from django.conf import settings
from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, AuthorFactory
from lotus.utils.tests import html_pyquery


# Shortcuts for shorter variable names
ADMINMODE_ARG = settings.LOTUS_ADMINMODE_URLARG
ADMINMODE_CONTEXTVAR = settings.LOTUS_ADMINMODE_CONTEXTVAR


def test_author_view_list(db, client):
    """
    Author list should be correctly ordered and paginated.
    """
    expected_pages = 2
    total_items = settings.LOTUS_AUTHOR_PAGINATION * expected_pages

    # Create a batch of author with numerated name on two digits to enforce sorting
    authors = []
    for i in range(1, total_items + 1):
        indice = str(i).zfill(2)
        name = "Foo_{}".format(indice)
        authors.append(
            AuthorFactory(
                username=name,
                first_name="Foo",
                last_name=indice,
            )
        )

    # Author need at least a published article to be "active"
    ArticleFactory(title="Sample", fill_authors=authors)

    # Additional author which are invisible because it does not have any published
    # article
    nietman = AuthorFactory(username="niet")
    ArticleFactory(title="Nope", status=STATUS_DRAFT, fill_authors=[nietman])

    # Expected items in page are simply ordered on name
    expected_item_page_1 = [
        v.get_full_name()
        for v in authors[0:settings.LOTUS_AUTHOR_PAGINATION]
    ]
    expected_item_page_2 = [
        v.get_full_name()
        for v in authors[settings.LOTUS_AUTHOR_PAGINATION:total_items]
    ]

    # Get first index page
    urlname = "lotus:author-index"
    response = client.get(reverse(urlname))
    assert response.status_code == 200

    # Parse first page HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .author-list-container .list .author")
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


def test_author_view_detail_404(db, client):
    """
    Trying to get unexisting Author should return a 404 response.
    """
    # Create a dummy object to get a correct URL then delete it
    dummy = AuthorFactory()
    url = dummy.get_absolute_url()
    dummy.delete()

    response = client.get(url)
    assert response.status_code == 404


def test_author_view_detail_for_empty(db, client):
    """
    Even it is not listed since it does not have any related article, author detail
    is still reachable.
    """
    # Create a dummy object to get a correct URL then delete it
    dummy = AuthorFactory()
    url = dummy.get_absolute_url()

    response = client.get(url)
    assert response.status_code == 200


def test_author_view_detail_admin_mode(db, admin_client, client):
    """
    Detail view should have context variable "admin_mode" with correct value according
    to the user and possible URL argument.
    """
    ping = AuthorFactory()

    # Anonymous are never allowed for admin mode
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[ADMINMODE_CONTEXTVAR] is False

    response = client.get(ping.get_absolute_url(), {ADMINMODE_ARG: 1})
    assert response.status_code == 200
    assert response.context[ADMINMODE_CONTEXTVAR] is False

    # Basic authenticated users are never allowed for admin mode
    user = AuthorFactory()
    client.force_login(user)
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[ADMINMODE_CONTEXTVAR] is False

    response = client.get(ping.get_absolute_url(), {ADMINMODE_ARG: 1})
    assert response.status_code == 200
    assert response.context[ADMINMODE_CONTEXTVAR] is False

    # Staff user is only allowed for admin mode if it request for it with correct URL
    # argument
    response = admin_client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[ADMINMODE_CONTEXTVAR] is False

    response = admin_client.get(ping.get_absolute_url(), {ADMINMODE_ARG: 1})
    assert response.status_code == 200
    assert response.context[ADMINMODE_CONTEXTVAR] is True


@freeze_time("2012-10-15 10:00:00")
@pytest.mark.parametrize("user_kind,client_kwargs,expected", [
    (
        "anonymous",
        {},
        ["Sample"],
    ),
    (
        "anonymous",
        {"admin": 1},
        ["Sample"],
    ),
    (
        "user",
        {},
        ["Private eye only", "Sample"],
    ),
    (
        "user",
        {"admin": 1},
        ["Private eye only", "Sample"],
    ),
    (
        "admin",
        {},
        ["Private eye only", "Sample"],
    ),
    (
        "admin",
        {"admin": 1},
        ["Tomorrow", "Niet", "Nope", "Private eye only", "Sample", "Yesterday"],
    ),
])
def test_author_view_detail_content(db, admin_client, client, user_kind,
                                    client_kwargs, expected):
    """
    Detail should contains expected content and the admin mode should be respected.

    We just superficially test article cases since they are already covered from
    article and category tests.
    """
    # Available Django clients as a dict to be able to switch on
    client_for = {
        "anonymous": client,
        "user": client,
        "admin": admin_client,
    }

    # Date references
    default_tz = pytz.timezone("UTC")
    yesterday = default_tz.localize(datetime.datetime(2012, 10, 14, 10, 0))
    tomorrow = default_tz.localize(datetime.datetime(2012, 10, 16, 10, 0))

    picsou = AuthorFactory()
    nobody = AuthorFactory(username="nobody")

    ArticleFactory(title="Sample", fill_authors=[picsou])

    # Not related to picsou user
    ArticleFactory(title="For nobody", fill_authors=[nobody])
    # For authenticated user only
    ArticleFactory(title="Private eye only", private=True, fill_authors=[picsou])
    # Only available in admin mode
    ArticleFactory(title="Nope", status=STATUS_DRAFT, fill_authors=[picsou])
    ArticleFactory(title="Niet", status=STATUS_DRAFT, fill_authors=[picsou, nobody])
    ArticleFactory(title="Yesterday", fill_authors=[picsou], publish_end=yesterday)
    ArticleFactory(
        title="Tomorrow",
        fill_authors=[picsou],
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )

    # Select the right client to use for user kind
    enabled_client = client_for[user_kind]
    # We have to force authenticated user (non admin)
    if user_kind == "user":
        user = AuthorFactory()
        client.force_login(user)

    url = picsou.get_absolute_url()
    response = enabled_client.get(url, client_kwargs)

    assert response.status_code == 200

    # from lotus.utils.tests import decode_response_or_string
    # print()
    # print(decode_response_or_string(response))
    # print()

    # Parse HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .articles .article")

    # Get useful content from list items
    content = []
    for item in items:
        title = item.cssselect(".title")[0].text
        content.append(title)

    assert content == expected


def test_author_view_detail_pagination(db, client):
    """
    Author detail should paginate its article list
    """
    # Our main category to test
    picsou = AuthorFactory()

    # No more articles than pagination limit
    ArticleFactory.create_batch(
        settings.LOTUS_ARTICLE_PAGINATION,
        fill_authors=[picsou],
    )

    # Get detail page
    url = picsou.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200

    # Parse HTML
    dom = html_pyquery(response)
    pagination = dom.find("#lotus-content .articles .pagination")

    # No pagination HTML is displayed when limit have not been reached
    assert len(pagination) == 0

    # Additional article to activate pagination
    ArticleFactory(fill_authors=[picsou])

    # With pagination activated there is at least two pages
    url = picsou.get_absolute_url()
    response = client.get(url)
    dom = html_pyquery(response)
    links = dom.find("#lotus-content .articles .pagination a")
    assert len(links) == 2

    # Ensure the second page only have the remaining item
    page_2_arg = links[1].get("href")
    url = picsou.get_absolute_url() + page_2_arg
    response = client.get(url)
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .articles .article")
    assert len(items) == 1
