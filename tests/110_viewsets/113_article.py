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
from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory, TagFactory, multilingual_article,
)

try:
    import rest_framework  # noqa: F401
except ModuleNotFoundError:
    API_AVAILABLE = False
else:
    API_AVAILABLE = True


pytestmark = pytest.mark.skipif(
    not API_AVAILABLE,
    reason="Django REST is not available, API is disabled"
)


# Shortcuts for shorter variable names
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
STATE_PREFIX = "article--"


@freeze_time("2012-10-15 10:00:00")
def test_article_viewset_list_payload(db, settings, api_client):
    """
    Article list item payload should contain fields as expected
    """
    cover_path = settings.LOTUS_API_TEST_BASEURL + "/media/lotus/article/cover/"

    # Date references
    utc = ZoneInfo("UTC")
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)

    author = AuthorFactory(first_name="Picsou", last_name="McDuck")
    category = CategoryFactory(title="cat_1")
    tag = TagFactory(name="Bingo", slug="bingo")

    article = ArticleFactory(
        title="Hello",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        fill_categories=[category],
        fill_authors=[author],
        fill_tags=[tag],
    )

    url = reverse("lotus-api:article-list")

    response = api_client.get(url)
    assert response.status_code == 200

    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))

    assert json_data["count"] == 1
    payload_item = json_data["results"][0]

    # Test categories fields
    categories = payload_item.pop("categories")
    assert len(categories) == 1
    assert list(categories[0].keys()) == [
        "url", "detail_url", "language", "title", "lead", "cover"
    ]

    # Test authors fields
    authors = payload_item.pop("authors")
    assert len(authors) == 1
    assert list(authors[0].keys()) == [
        "url", "detail_url", "first_name", "last_name"
    ]

    # Test tag names
    tags = payload_item.pop("tags")
    assert len(tags) == 1
    assert isinstance(tags[0], str) is True

    # Test cover path apart
    cover = payload_item.pop("cover")
    assert cover.startswith(cover_path) is True

    # Test remaining fields
    assert payload_item == {
        "detail_url": article.get_absolute_url(),
        "introduction": article.introduction,
        "language": article.language,
        "publish_datetime": article.publish_datetime().isoformat(),
        "seo_title": article.seo_title,
        "slug": article.slug,
        "states": [STATES["status_available"]],
        "title": article.title,
        "url": settings.LOTUS_API_TEST_BASEURL + "/api/article/1/",
    }


@freeze_time("2012-10-15 10:00:00")
@pytest.mark.parametrize("user_kind, with_preview, expected", [
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
])
def test_article_viewset_list_publication(db, api_client, user_kind, with_preview,
                                          expected):
    """
    This is alike 'test_article_view_list_publication' except preview mode is not
    checked.
    """
    # We have to force authentication for user or admin
    if user_kind == "user":
        user = AuthorFactory()
        api_client.force_authenticate(user=user)
    elif user_kind == "admin":
        user = AuthorFactory(flag_is_admin=True)
        api_client.force_authenticate(user=user)

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

    url = reverse("lotus-api:article-list")

    response = api_client.get(url)
    assert response.status_code == 200

    json_data = response.json()
    assert json_data["count"] == len(expected)
    # This test never have enough items to trigger pagination
    assert json_data["next"] is None
    assert json_data["previous"] is None

    assert [
        [item["title"], item["states"]]
        for item in json_data["results"]
    ] == expected


@pytest.mark.parametrize("allow", [True, False])
def test_article_viewset_language(db, settings, api_client, allow):
    """
    Viewset should returns content for required language by client.

    This also demonstrate the way to ask for language in a request to Lotus API with
    the HTTP header 'Accept-Language'.
    """
    settings.LANGUAGE_CODE = "en"
    settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE = allow

    # Create a single category used everywhere to avoid create multiple random ones
    # from factory
    ping = CategoryFactory(slug="ping")

    # Create bread articles with published FR translation
    multilingual_article(
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

    url = reverse("lotus-api:article-list")

    response = api_client.get(url)
    assert response.status_code == 200

    # List result for default language (english)
    json_data = response.json()
    # print()
    # print(json.dumps(json_data, indent=4))
    assert len(json_data["results"]) == 2
    assert len([
        article
        for article in json_data["results"]
        if article["language"] == "en"
    ]) == 2

    # List result for french language returns only french article
    response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="fr")
    json_data = response.json()
    assert response.status_code == 200
    assert len(json_data["results"]) == 2
    assert len([
        article
        for article in json_data["results"]
        if article["language"] == "fr"
    ]) == 2

    # List result for deutsch language returns only deutsch article
    response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="de")
    json_data = response.json()
    assert response.status_code == 200
    assert len(json_data["results"]) == 1
    assert len([
        article
        for article in json_data["results"]
        if article["language"] == "de"
    ]) == 1

    # List result for unavailable language fallback on default site language
    response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="zh")
    json_data = response.json()
    assert response.status_code == 200
    assert len(json_data["results"]) == 2
    assert len([
        article
        for article in json_data["results"]
        if article["language"] == "en"
    ]) == 2

    # Details result with default language
    detail_url = created_cheese["original"].get_absolute_api_url()
    response = api_client.get(detail_url)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, dict) is True
    assert json_data["url"] == "http://testserver" + detail_url
    assert json_data["language"] == created_cheese["original"].language
    assert json_data["title"] == created_cheese["original"].title

    # Details result for french language
    detail_url = created_cheese["translations"]["fr"].get_absolute_api_url()
    response = api_client.get(detail_url, HTTP_ACCEPT_LANGUAGE="fr")
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, dict) is True
    assert json_data["url"] == "http://testserver" + detail_url
    assert json_data["language"] == created_cheese["translations"]["fr"].language
    assert json_data["title"] == created_cheese["translations"]["fr"].title


def test_article_viewset_allow_language_safe_enabled(db, settings, api_client):
    """
    When setting 'LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE' is enabled the detail won't
    filter on current client language, an object in different language can be reached.
    """
    settings.LANGUAGE_CODE = "en"
    settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE = True

    category = CategoryFactory(slug="ping", language="en")
    categorie = CategoryFactory(slug="pong", language="fr")

    hello = ArticleFactory(title="Hello", language="en", fill_categories=[category])
    salut = ArticleFactory(title="Salut", language="fr", fill_categories=[categorie])

    # English article is reachable with english language
    response = api_client.get(hello.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 200

    # French article is still reachable with english language
    response = api_client.get(salut.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 200


def test_article_viewset_allow_language_safe_disabled(db, settings, api_client):
    """
    When setting 'LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE' is disabled the detail will
    filter on current client language, an object in different language can not be
    reached.
    """
    settings.LANGUAGE_CODE = "en"
    settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE = False

    category = CategoryFactory(slug="ping", language="en")
    categorie = CategoryFactory(slug="pong", language="fr")

    hello = ArticleFactory(title="Hello", language="en", fill_categories=[category])
    salut = ArticleFactory(title="Salut", language="fr", fill_categories=[categorie])

    response = api_client.get(hello.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 200

    response = api_client.get(salut.get_absolute_api_url(), HTTP_ACCEPT_LANGUAGE="en")
    assert response.status_code == 404
