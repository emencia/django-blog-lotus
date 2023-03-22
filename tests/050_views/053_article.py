import datetime
from pathlib import Path

import pytest
from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from sorl.thumbnail.conf import settings as sorl_settings

from django.conf import settings
from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory, TagFactory, multilingual_article,
)
from lotus.utils.tests import get_admin_change_url, html_pyquery


# Shortcuts for shorter variable names
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
STATE_PREFIX = "article--"


def test_article_view_list_preview_mode(
    db, settings, admin_client, client, enable_preview
):
    """
    List view should have context variable for preview mode with correct value according
    to the user and possible URL argument.

    TODO:
        Make the same for detail view
    """
    urlname = "lotus:article-index"

    ArticleFactory()

    # Anonymous are never allowed for preview mode
    response = client.get(reverse(urlname))
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    enable_preview(client)
    response = client.get(reverse(urlname))
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    # Basic authenticated users are never allowed for preview mode
    user = AuthorFactory()
    client.force_login(user)
    response = client.get(reverse(urlname))
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    enable_preview(client)
    response = client.get(reverse(urlname))
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    # Staff user is only allowed for preview mode if it request for it with correct URL
    # argument
    response = admin_client.get(reverse(urlname))
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    enable_preview(admin_client)
    response = admin_client.get(reverse(urlname))
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is True


@freeze_time("2012-10-15 10:00:00")
@pytest.mark.parametrize("user_kind,with_preview,expected", [
    (
        "anonymous",
        False,
        [
            # Expected title and CSS classes
            [
                "05. pinned, published past hour",
                [STATES["pinned"], STATES["status_available"]],
            ],
            [
                "04. published past hour",
                [STATES["status_available"]]
            ],
            [
                "06. featured, published past hour",
                [STATES["featured"], STATES["status_available"]],
            ],
            [
                "08. published past hour, end next hour",
                [STATES["status_available"]]
            ],
            [
                "02. published yesterday",
                [STATES["status_available"]]
            ],
        ],
    ),
    (
        "anonymous",
        True,
        [
            # Expected title and CSS classes
            [
                "05. pinned, published past hour",
                [STATES["pinned"], STATES["status_available"]],
            ],
            [
                "04. published past hour",
                [STATES["status_available"]]
            ],
            [
                "06. featured, published past hour",
                [STATES["featured"], STATES["status_available"]],
            ],
            [
                "08. published past hour, end next hour",
                [STATES["status_available"]]
            ],
            [
                "02. published yesterday",
                [STATES["status_available"]]
            ],
        ],
    ),
    (
        "user",
        False,
        [
            # Expected title and CSS classes
            [
                "05. pinned, published past hour",
                [STATES["pinned"], STATES["status_available"]],
            ],
            [
                "04. published past hour",
                [STATES["status_available"]]
            ],
            [
                "06. featured, published past hour",
                [STATES["featured"], STATES["status_available"]],
            ],
            [
                "07. private, published past hour",
                [STATES["private"], STATES["status_available"]],
            ],
            [
                "08. published past hour, end next hour",
                [STATES["status_available"]]
            ],
            [
                "02. published yesterday",
                [STATES["status_available"]]
            ],
        ],
    ),
    (
        "user",
        True,
        [
            # Expected title and CSS classes
            [
                "05. pinned, published past hour",
                [STATES["pinned"], STATES["status_available"]],
            ],
            [
                "04. published past hour",
                [STATES["status_available"]]
            ],
            [
                "06. featured, published past hour",
                [STATES["featured"], STATES["status_available"]],
            ],
            [
                "07. private, published past hour",
                [STATES["private"], STATES["status_available"]],
            ],
            [
                "08. published past hour, end next hour",
                [STATES["status_available"]]
            ],
            [
                "02. published yesterday",
                [STATES["status_available"]]
            ],
        ],
    ),
    (
        "admin",
        False,
        [
            # Expected title and CSS classes
            [
                "05. pinned, published past hour",
                [STATES["pinned"], STATES["status_available"]],
            ],
            [
                "04. published past hour",
                [STATES["status_available"]]
            ],
            [
                "06. featured, published past hour",
                [STATES["featured"], STATES["status_available"]],
            ],
            [
                "07. private, published past hour",
                [STATES["private"], STATES["status_available"]],
            ],
            [
                "08. published past hour, end next hour",
                [STATES["status_available"]]
            ],
            [
                "02. published yesterday",
                [STATES["status_available"]]
            ],
        ],
    ),
    (
        "admin",
        True,
        [
            # Expected title and CSS classes
            [
                "05. pinned, published past hour",
                [STATES["pinned"], STATES["status_available"]],
            ],
            [
                "09. publish next hour",
                [STATES["status_available"], STATES["publish_start_below"]],
            ],
            [
                "10. publish next hour, end tomorrow",
                [STATES["status_available"], STATES["publish_start_below"]],
            ],
            [
                "04. published past hour",
                [STATES["status_available"]]
            ],
            [
                "06. featured, published past hour",
                [STATES["featured"], STATES["status_available"]],
            ],
            [
                "07. private, published past hour",
                [STATES["private"], STATES["status_available"]],
            ],
            [
                "08. published past hour, end next hour",
                [STATES["status_available"]]
            ],
            [
                "01. draft yesterday",
                [STATES["status_draft"]]
            ],
            [
                "02. published yesterday",
                [STATES["status_available"]]
            ],
            [
                "03. published yesterday, ended one hour ago",
                [STATES["status_available"], STATES["publish_end_passed"]],
            ],
        ],
    ),
])
def test_article_view_list_publication(
    db, admin_client, client, enable_preview, user_kind, with_preview, expected
):
    """
    View list should respect publication criterias (dates and state, private article and
    order.

    Tested against profiles:

    * non authenticated;
    * non authenticated trying to use preview mode;
    * authenticated basic user;
    * authenticated basic user trying to use preview mode;
    * admin without preview mode;
    * admin with preview mode;
    """
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

    # Select the right client to use for user kind
    enabled_client = client_for[user_kind]
    # We have to force authenticated user (non admin)
    if user_kind == "user":
        user = AuthorFactory()
        client.force_login(user)

    if with_preview:
        enable_preview(enabled_client)

    # Get all available items from HTML page
    urlname = "lotus:article-index"
    response = enabled_client.get(reverse(urlname))
    assert response.status_code == 200

    # Parse HTML
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .article-list-container .list .article")

    # Get useful content from list items
    content = []
    for item in items:
        title = item.cssselect(".title")[0].text
        # Drop item class since it's useless for test
        classes = [
            v.replace(STATE_PREFIX, "")
            for v in item.get("class").split()
            if v.replace(STATE_PREFIX, "") in available_state_classes
        ]
        content.append([title, classes])

    assert content == expected


def test_article_view_detail_published(db, admin_client, client):
    """
    Published article is reachable from anyone.
    """
    instance = ArticleFactory()

    response = client.get(instance.get_absolute_url())
    assert response.status_code == 200

    response = admin_client.get(instance.get_absolute_url())
    assert response.status_code == 200


def test_article_view_detail_draft(db, admin_client, client, enable_preview):
    """
    Draft article is only reachable for admin in 'preview mode'.
    """
    user = AuthorFactory()
    instance = ArticleFactory(status=STATUS_DRAFT)

    # With default behavior a draft is not available no matter it's for an admin or not
    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    response = admin_client.get(instance.get_absolute_url())
    assert response.status_code == 404

    # Switch user to preview mode
    enable_preview(client)

    # Preview mode behavior do not work for non admin users
    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    client.force_login(user)
    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    # Switch admin to preview mode
    enable_preview(admin_client)

    # Preview mode behavior only work for admin users
    response = admin_client.get(instance.get_absolute_url())
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


@freeze_time("2012-10-15 10:00:00")
def test_article_view_detail_publication(db, admin_client, client, enable_preview):
    """
    Publication criteria should be respected to view an Article, excepted for admin
    mode.
    """
    utc = ZoneInfo("UTC")
    past_hour = datetime.datetime(2012, 10, 15, 9, 00).replace(tzinfo=utc)

    instance = ArticleFactory(publish_end=past_hour)

    response = client.get(instance.get_absolute_url())
    assert response.status_code == 404

    # Switch user to preview mode
    enable_preview(admin_client)

    response = admin_client.get(instance.get_absolute_url())
    assert response.status_code == 200


def test_article_view_detail_preview_mode(
    db, settings, admin_client, client, enable_preview
):
    """
    Detail view should have context variable for preview mode with correct value
    according to the user and possible URL argument.
    """
    ping = ArticleFactory()

    # Anonymous are never allowed for preview mode
    response = client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    # Switch user to preview mode
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

    # Staff user is only allowed for preview mode if it request for it with correct URL
    # argument
    response = admin_client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is False

    # Switch user to preview mode
    enable_preview(admin_client)

    response = admin_client.get(ping.get_absolute_url())
    assert response.status_code == 200
    assert response.context[settings.LOTUS_PREVIEW_VARNAME] is True


def test_article_view_detail_content(db, admin_client, enable_preview):
    """
    Detail view should contain all expected content and relations.

    Note we are requesting with preview mode to be able to see a draft
    article to check for the "draft" CSS class.

    Also, this does not care about textual content (title, lead, content, etc..).
    """
    SORL_CACHE_PATH = str(
        Path(settings.MEDIA_URL) / Path(sorl_settings.THUMBNAIL_PREFIX)
    )

    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")
    AuthorFactory(first_name="Flairsou", last_name="Cresus")

    cat_1 = CategoryFactory(title="cat_1")
    CategoryFactory(title="cat_2")
    CategoryFactory(title="cat_3")

    bingo = TagFactory(name="Bingo", slug="bingo")
    TagFactory(name="Nope", slug="nope")

    ArticleFactory(title="Foo")
    article_2 = ArticleFactory(title="Bar")
    article_3 = ArticleFactory(
        title="Ping",
        fill_categories=[cat_1],
        fill_related=[article_2],
        fill_authors=[picsou],
        fill_tags=[bingo],
        status=STATUS_DRAFT,
        pinned=True,
        featured=True,
        private=True,
    )

    # Switch user to preview mode
    enable_preview(admin_client)

    # Get detail HTML page
    response = admin_client.get(article_3.get_absolute_url())
    assert response.status_code == 200

    # Parse HTML response to get content and relations
    dom = html_pyquery(response)
    container = dom.find("#lotus-content .article-detail")[0]

    categories = [
        item.text.strip()
        for item in dom.find("#lotus-content .categories li a")
    ]
    assert categories == ["cat_1"]

    authors = [item.text.strip() for item in dom.find("#lotus-content .authors li a")]
    assert authors == ["Picsou McDuck"]

    relateds = [
        item.text.strip()
        for item in dom.find("#lotus-content .relateds li a")
    ]
    assert relateds == ["Bar"]

    tags = [item.text.strip() for item in dom.find("#lotus-content .tags div a")]
    assert tags == ["Bingo"]

    cover_link = dom.find("#lotus-content .cover a")[0].get("href")
    cover_img = dom.find("#lotus-content .cover img")[0].get("src")
    assert cover_link == article_3.cover.url
    assert cover_img.startswith(SORL_CACHE_PATH) is True

    large_link = dom.find("#lotus-content .image a")[0].get("href")
    large_img = dom.find("#lotus-content .image img")[0].get("src")
    assert large_link == article_3.image.url
    assert large_img.startswith(SORL_CACHE_PATH) is True

    classes = sorted([
        v.replace(STATE_PREFIX, "") for v in container.get("class").split()
        if v != "article-detail"
    ])
    assert classes == [
        STATES["status_draft"], STATES["featured"], STATES["pinned"], STATES["private"],
    ]


def test_article_view_detail_metas(db, client):
    """
    Detail page should have the right metas content.
    """
    # No specific SEO content
    article_noseo = ArticleFactory(
        title="Ping",
        lead="",
    )
    # Fill all the SEO fields
    article_seo = ArticleFactory(
        title="Bar",
        seo_title="Meow",
        lead="Pwet pwet",
    )

    # Parse HTML response for 'no SEO article'
    response = client.get(article_noseo.get_absolute_url())
    assert response.status_code == 200

    dom = html_pyquery(response)
    meta_title = dom.find("head title")[0]
    meta_description = dom.find("head meta[name='description']")

    assert meta_title.text == "Ping"
    assert len(meta_description) == 0

    # Parse HTML response for 'SEO article'
    response = client.get(article_seo.get_absolute_url())
    assert response.status_code == 200

    dom = html_pyquery(response)
    meta_title = dom.find("head title")[0]
    meta_description = dom.find("head meta[name='description']")

    assert meta_title.text == "Meow"
    assert len(meta_description) == 1
    assert meta_description[0].get("content") == "Pwet pwet"


def test_article_view_preview(db, client, admin_client):
    """
    Preview view should only be reachable from admin and return a success response for
    any article, published or not.
    """
    user = AuthorFactory()

    published = ArticleFactory()
    draft = ArticleFactory(status=STATUS_DRAFT)

    # For anonymous user
    response = client.get(published.get_absolute_preview_url())
    assert response.status_code == 403

    response = client.get(draft.get_absolute_preview_url())
    assert response.status_code == 403

    # For authenticated user
    client.force_login(user)
    response = client.get(published.get_absolute_preview_url())
    assert response.status_code == 403

    response = client.get(draft.get_absolute_preview_url())
    assert response.status_code == 403

    # For admin
    response = admin_client.get(published.get_absolute_preview_url())
    assert response.status_code == 200

    response = admin_client.get(draft.get_absolute_preview_url())
    assert response.status_code == 200


def check_detail_links(client_obj, article):
    """
    Internal helper to get links from article detail for a client object.

    Always perform a request.
    """
    response = client_obj.get(article.get_absolute_url())
    assert response.status_code == 200

    dom = html_pyquery(response)
    container = dom.find("#lotus-content .article-detail")[0]

    link_edit = container.cssselect(".detail-edit")
    link_translate = container.cssselect(".detail-translate")

    return link_edit, link_translate


def test_article_view_detail_admin_links(db, settings, admin_client, client):
    """
    Detail sidebar should have the right links for admin depending article status.
    """
    # NOTE: A test playing with language and view requests must enforce default
    # language since LANGUAGE_CODE may be altered between two tests.
    settings.LANGUAGE_CODE = "en"

    # Create a single category used everywhere to avoid create multiple random ones
    # from factory
    ping = CategoryFactory(slug="ping")

    # Create bread articles with published FR translation
    created_bread = multilingual_article(
        title="Bread",
        slug="bread",
        langs=["fr"],
        fill_categories=[ping],
        contents={
            "fr": {
                "title": "Pain",
                "slug": "pain",
                "fill_categories": [ping],
            },
        },
    )

    # Create cheese articles with published FR and DE translations
    created_cheese = multilingual_article(
        title="Cheese",
        slug="cheese",
        langs=["fr", "de"],
        fill_categories=[ping],
        contents={
            "fr": {
                "title": "Fromage",
                "slug": "fromage",
                "fill_categories": [ping],
            },
            "de": {
                "title": "Käse",
                "slug": "kase",
                "fill_categories": [ping],
            }
        },
    )

    # Parse Cheese versions with anonymous to search for links
    ano_cheese_en_links = check_detail_links(
        client,
        created_cheese["original"]
    )
    ano_cheese_fr_links = check_detail_links(
        client,
        created_cheese["translations"]["fr"]
    )
    # Nothing is available to non admin
    assert ano_cheese_en_links == ([], [])
    assert ano_cheese_fr_links == ([], [])

    # Parse Cheese versions with admin to search for links
    admin_cheese_en_links = check_detail_links(
        admin_client,
        created_cheese["original"]
    )
    admin_cheese_fr_links = check_detail_links(
        admin_client,
        created_cheese["translations"]["fr"]
    )
    # 'Edit' link is available but not 'translate' since there is no language left
    assert admin_cheese_en_links[0][0].get("href") == get_admin_change_url(
        created_cheese["original"]
    )
    assert len(admin_cheese_en_links[1]) == 0
    assert admin_cheese_fr_links[0][0].get("href") == get_admin_change_url(
        created_cheese["translations"]["fr"]
    )
    assert len(admin_cheese_fr_links[1]) == 0

    # Parse Bread versions with anonymous to search for links
    ano_bread_en_links = check_detail_links(
        client,
        created_bread["original"]
    )
    ano_bread_fr_links = check_detail_links(
        client,
        created_bread["translations"]["fr"]
    )
    # Nothing is available to non admin
    assert ano_bread_en_links == ([], [])
    assert ano_bread_fr_links == ([], [])

    # Parse Bread versions with admin to search for links
    admin_bread_en_links = check_detail_links(
        admin_client,
        created_bread["original"]
    )
    admin_bread_fr_links = check_detail_links(
        admin_client,
        created_bread["translations"]["fr"]
    )
    # 'Edit' and 'translate' links are available since there is a language left (de)
    assert admin_bread_en_links[0][0].get("href") == get_admin_change_url(
        created_bread["original"]
    )
    assert len(admin_bread_en_links[1]) == 1
    assert admin_bread_en_links[1][0].get("href") == reverse(
        "admin:lotus_article_translate_original",
        args=[
            created_bread["original"].pk
        ]
    )
    assert admin_bread_fr_links[0][0].get("href") == get_admin_change_url(
        created_bread["translations"]["fr"]
    )
    assert admin_bread_fr_links[1][0].get("href") == reverse(
        "admin:lotus_article_translate_original",
        args=[
            created_bread["translations"]["fr"].pk
        ]
    )
