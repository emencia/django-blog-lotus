import datetime

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

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, AuthorFactory
from lotus.utils.tests import html_pyquery


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

    # Additional authors that are invisibles because they does not have any published
    # article for anonymous
    ArticleFactory(title="Nope", status=STATUS_DRAFT, fill_authors=[
        AuthorFactory(username="niet")
    ])
    ArticleFactory(title="Private", private=True, fill_authors=[
        AuthorFactory(username="spy")
    ])

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


def test_author_view_detail_preview_mode(
    db, settings, admin_client, client, enable_preview
):
    """
    Detail view should have context variable for preview mode with correct value
    according to the user and possible URL argument.
    """
    ping = AuthorFactory()

    # Anonymous are never allowed for preview mode
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    enable_preview(client)
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    # Basic authenticated users are never allowed for preview mode
    user = AuthorFactory()
    client.force_login(user)
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    enable_preview(client)
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    # Staff user is only allowed for preview mode if it request for it with correct URL
    # argument
    response = admin_client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    enable_preview(admin_client)
    response = admin_client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is True


@freeze_time("2012-10-15 10:00:00")
@pytest.mark.parametrize("user_kind,with_preview,expected", [
    (
        "anonymous",
        False,
        ["Sample"],
    ),
    (
        "anonymous",
        True,
        ["Sample"],
    ),
    (
        "user",
        False,
        ["Private eye only", "Sample"],
    ),
    (
        "user",
        True,
        ["Private eye only", "Sample"],
    ),
    (
        "admin",
        False,
        ["Private eye only", "Sample"],
    ),
    (
        "admin",
        True,
        ["Tomorrow", "Niet", "Nope", "Private eye only", "Sample", "Yesterday"],
    ),
])
def test_author_view_detail_content(
    db, admin_client, client, enable_preview, user_kind, with_preview, expected
):
    """
    Detail should contains expected content and the preview mode should be respected.

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
    utc = ZoneInfo("UTC")
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    picsou = AuthorFactory()
    nobody = AuthorFactory(username="nobody")

    ArticleFactory(title="Sample", fill_authors=[picsou])

    # Not related to picsou user
    ArticleFactory(title="For nobody", fill_authors=[nobody])
    # For authenticated user only
    ArticleFactory(title="Private eye only", private=True, fill_authors=[picsou])
    # Only available in preview mode
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

    if with_preview:
        enable_preview(enabled_client)

    url = picsou.get_absolute_url()
    response = enabled_client.get(url)

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
