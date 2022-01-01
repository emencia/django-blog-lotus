import pytest

from django.conf import settings
from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, AuthorFactory, CategoryFactory
from lotus.utils.tests import html_pyquery
from lotus.views import AdminModeMixin


# Shortcuts for shorter variable names
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
ADMINMODE_ARG = AdminModeMixin.adminmode_argument_name


def test_category_view_list(db, client):
    """
    Category list should be correctly ordered and paginated.
    """
    expected_pages = 2
    total_items = settings.LOTUS_CATEGORY_PAGINATION * expected_pages

    # Create a batch of category with numerated name on two digit filled with
    # leading 0 to enforce sorting
    names = [
        "{}.Foo".format(str(i).zfill(2))
        for i in range(1, total_items + 1)
    ]
    for item in names:
        CategoryFactory(title=item)

    # Expected items in page are simply ordered on name
    expected_item_page_1 = names[0:settings.LOTUS_CATEGORY_PAGINATION]
    expected_item_page_2 = names[settings.LOTUS_CATEGORY_PAGINATION:total_items]

    # Get detail for first page
    urlname = "lotus:category-index"
    response = client.get(reverse(urlname))
    assert response.status_code == 200

    # Parse first page HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .category-list-container .list .category")
    links = dom.find("#lotus-content .category-list-container .pagination a")
    # Get item titles
    link_title_page_1 = []
    for item in items:
        link_title_page_1.append(item.cssselect(".title")[0].text)

    # Expected pagination links
    assert len(links) == 2
    # Expected paginated item list length
    assert len(items) == settings.LOTUS_CATEGORY_PAGINATION
    # Ensure every expected items are here respecting order
    assert expected_item_page_1 == link_title_page_1

    # Get detail for second page
    urlname = "lotus:category-index"
    response = client.get(reverse(urlname), {"page": 2})
    assert response.status_code == 200

    # Parse second page HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .category-list-container .list .category")
    # Get item titles
    link_title_page_2 = []
    for item in items:
        link_title_page_2.append(item.cssselect(".title")[0].text)

    # Ensure every expected items are here respecting order
    assert expected_item_page_2 == link_title_page_2


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


def test_category_view_detail_admin_mode(db, admin_client, client):
    """
    Detail view should have context variable "admin_mode" with correct value according
    to the user and possible URL argument.
    """
    ping = CategoryFactory()

    # Anonymous are never allowed for admin mode
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[AdminModeMixin.adminmode_context_name] is False

    response = client.get(ping.get_absolute_url(), {ADMINMODE_ARG: 1})
    assert response.status_code == 200
    assert response.context[AdminModeMixin.adminmode_context_name] is False

    # Basic authenticated users are never allowed for admin mode
    user = AuthorFactory()
    client.force_login(user)
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[AdminModeMixin.adminmode_context_name] is False

    response = client.get(ping.get_absolute_url(), {ADMINMODE_ARG: 1})
    assert response.status_code == 200
    assert response.context[AdminModeMixin.adminmode_context_name] is False

    # Staff user is only allowed for admin mode if it request for it with correct URL
    # argument
    response = admin_client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[AdminModeMixin.adminmode_context_name] is False

    response = admin_client.get(ping.get_absolute_url(), {ADMINMODE_ARG: 1})
    assert response.status_code == 200
    assert response.context[AdminModeMixin.adminmode_context_name] is True


@pytest.mark.parametrize("user_kind,client_kwargs,expected", [
    (
        "anonymous",
        {},
        [
            # Expected title and CSS classes
            ["Pinned", [STATES["pinned"], STATES["status_available"]]],
            ["Featured", [STATES["featured"], STATES["status_available"]]],
            ["06. Plip", [STATES["status_available"]]],
            ["05. Plop", [STATES["status_available"]]],
            ["04. Pong", [STATES["status_available"]]],
            ["03. Ping", [STATES["status_available"]]],
            ["02. Bar", [STATES["status_available"]]],
            ["01. Foo", [STATES["status_available"]]],
        ],
    ),
    (
        "anonymous",
        {ADMINMODE_ARG: 1},
        [
            # Expected title and CSS classes
            ["Pinned", [STATES["pinned"], STATES["status_available"]]],
            ["Featured", [STATES["featured"], STATES["status_available"]]],
            ["06. Plip", [STATES["status_available"]]],
            ["05. Plop", [STATES["status_available"]]],
            ["04. Pong", [STATES["status_available"]]],
            ["03. Ping", [STATES["status_available"]]],
            ["02. Bar", [STATES["status_available"]]],
            ["01. Foo", [STATES["status_available"]]],
        ],
    ),
    (
        "user",
        {},
        [
            # Expected title and CSS classes
            ["Pinned", [STATES["pinned"], STATES["status_available"]]],
            ["Featured", [STATES["featured"], STATES["status_available"]]],
            ["06. Plip", [STATES["status_available"]]],
            ["05. Plop", [STATES["status_available"]]],
            ["04. Pong", [STATES["status_available"]]],
            ["03. Ping", [STATES["status_available"]]],
            ["02. Bar", [STATES["status_available"]]],
            ["01. Foo", [STATES["status_available"]]],
            ["Private", [STATES["private"], STATES["status_available"]]],
        ],
    ),
    (
        "user",
        {ADMINMODE_ARG: 1},
        [
            # Expected title and CSS classes
            ["Pinned", [STATES["pinned"], STATES["status_available"]]],
            ["Featured", [STATES["featured"], STATES["status_available"]]],
            ["06. Plip", [STATES["status_available"]]],
            ["05. Plop", [STATES["status_available"]]],
            ["04. Pong", [STATES["status_available"]]],
            ["03. Ping", [STATES["status_available"]]],
            ["02. Bar", [STATES["status_available"]]],
            ["01. Foo", [STATES["status_available"]]],
            ["Private", [STATES["private"], STATES["status_available"]]],
        ],
    ),
    (
        "admin",
        {},
        [
            # Expected title and CSS classes
            ["Pinned", [STATES["pinned"], STATES["status_available"]]],
            ["Featured", [STATES["featured"], STATES["status_available"]]],
            ["06. Plip", [STATES["status_available"]]],
            ["05. Plop", [STATES["status_available"]]],
            ["04. Pong", [STATES["status_available"]]],
            ["03. Ping", [STATES["status_available"]]],
            ["02. Bar", [STATES["status_available"]]],
            ["01. Foo", [STATES["status_available"]]],
            ["Private", [STATES["private"], STATES["status_available"]]],
        ],
    ),
    (
        "admin",
        {ADMINMODE_ARG: 1},
        [
            # Expected title and CSS classes
            ["Pinned", [STATES["pinned"], STATES["status_available"]]],
            ["Featured", [STATES["featured"], STATES["status_available"]]],
            ["06. Plip", [STATES["status_available"]]],
            ["05. Plop", [STATES["status_available"]]],
            ["04. Pong", [STATES["status_available"]]],
            ["03. Ping", [STATES["status_available"]]],
            ["02. Bar", [STATES["status_available"]]],
            ["01. Foo", [STATES["status_available"]]],
            ["Private", [STATES["private"], STATES["status_available"]]],
            ["In draft", [STATES["status_draft"]]],
        ],
    ),
])
def test_category_view_detail_content(db, admin_client, client, user_kind,
                                      client_kwargs, expected):
    """
    Category detail page should have category contents and related articles following
    publication rules (as described in article list view tests).
    """
    STATE_PREFIX = "article--"
    # Available Django clients as a dict to be able to switch on
    client_for = {
        "anonymous": client,
        "user": client,
        "admin": admin_client,
    }

    # Available article state CSS class names to look for
    available_state_classes = [
        v
        for k, v in STATES.items()
    ]

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
    title = dom.find("#lotus-content .category-detail .title")[0].text
    cover = dom.find("#lotus-content .cover img")[0].get("src")

    assert title == picsou.title
    assert cover == picsou.cover.url

    # Get articles
    items = dom.find("#lotus-content .category-detail .articles .article")

    # Get useful content from list items
    content = []
    for item in items:
        title = item.cssselect(".title")[0].text
        # Drop item class since it's useless for test
        # NOTE: We clean out the state prefix which is defined on templatetag
        classes = [
            v.replace(STATE_PREFIX, "")
            for v in item.get("class").split()
            if v.replace(STATE_PREFIX, "") in available_state_classes
        ]
        content.append([title, classes])

    assert content == expected


def test_category_view_detail_pagination(db, client):
    """
    Category detail should paginate its article list
    """
    # Our main category to test
    picsou = CategoryFactory(title="Picsou", slug="picsou")

    # No more articles than pagination limit
    ArticleFactory.create_batch(
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
    items = dom.find("#lotus-content .category-detail .articles .article")
    assert len(items) == 1


def test_category_view_detail_metas(db, client):
    """
    Detail page should have the right metas content.
    """
    # No specific SEO content
    category_noseo = CategoryFactory(
        title="Picsou",
        lead="",
    )
    # Fill all the SEO fields
    category_seo = CategoryFactory(
        title="Donald",
        lead="Blah blah blah",
    )

    # Parse HTML response for 'no SEO category'
    url = category_noseo.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    meta_title = dom.find("head title")[0]
    meta_description = dom.find("head meta[name='description']")

    assert meta_title.text == "Picsou"
    assert len(meta_description) == 0

    # Parse HTML response for 'SEO category'
    url = category_seo.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    meta_title = dom.find("head title")[0]
    meta_description = dom.find("head meta[name='description']")

    assert meta_title.text == "Donald"
    assert len(meta_description) == 1
    assert meta_description[0].get("content") == "Blah blah blah"
