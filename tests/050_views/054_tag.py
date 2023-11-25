import datetime

from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.urls import translate_url, reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, AuthorFactory, TagFactory
from lotus.utils.tests import html_pyquery


@freeze_time("2012-10-15 10:00:00")
def test_tag_view_index(db, admin_client, client, enable_preview, settings):
    """
    Index view should list tags used in articles respecting publication criteria.

    Tested for:

    * Lambda user (anonymous) for default language;
    * Lambda user (anonymous) for french language;
    * Admin user with preview mode and for default language;

    """
    # NOTE: A test playing with language and view requests must enforce default
    # language since LANGUAGE_CODE may be altered between two tests.
    settings.LANGUAGE_CODE = "en"

    utc = ZoneInfo("UTC")
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    science = TagFactory(name="Science", slug="science")
    TagFactory(name="Sausage", slug="sausage")
    game = TagFactory(name="Game", slug="game")
    music = TagFactory(name="Music", slug="music")
    french_only = TagFactory(name="French only", slug="french-only")
    not_available = TagFactory(name="Not available", slug="not-available")
    TagFactory(name="Not used", slug="not-used")

    ArticleFactory(
        title="Foo",
        fill_tags=[science, game, music],
    )
    ArticleFactory(
        title="Bar",
        fill_tags=[science],
    )
    ArticleFactory(
        title="France",
        fill_tags=[game, french_only],
        language="fr",
    )
    ArticleFactory(
        title="Ping",
        fill_tags=[science, not_available],
        status=STATUS_DRAFT,
    )
    ArticleFactory(
        title="Pong",
        fill_tags=[game, not_available],
        private=True,
    )
    ArticleFactory(
        title="Pang",
        fill_tags=[music, not_available],
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )

    # Get tag index url for lambda user with defaut language 'en'
    url = reverse("lotus:tag-index")
    # Get page HTML
    response = client.get(url)
    assert response.status_code == 200
    # Parse HTML response  and build a summary from found items so we can easily make
    # assertion
    dom = html_pyquery(response)
    container = dom.find("#lotus-content .tag-list-container .list.container")[0]
    tags = [
        {
            "name": item.text.strip(),
            "count": int(item.cssselect("span")[0].text.strip()),
            "url": item.get("href"),
        }
        for item in container.cssselect("a")
    ]
    assert tags == [
        {
            "name": "Game",
            "count": 1,
            "url": "/en/tags/game/"
        },
        {
            "name": "Music",
            "count": 1,
            "url": "/en/tags/music/"
        },
        {
            "name": "Science",
            "count": 2,
            "url": "/en/tags/science/"
        }
    ]

    # Get tag index url for lambda user with defaut language 'fr'
    url = translate_url(reverse("lotus:tag-index"), "fr")
    # Get page HTML
    response = client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)
    container = dom.find("#lotus-content .tag-list-container .list.container")[0]
    tags = [
        {
            "name": item.text.strip(),
            "count": int(item.cssselect("span")[0].text.strip()),
            "url": item.get("href"),
        }
        for item in container.cssselect("a")
    ]
    assert tags == [
        {
            "name": "French only",
            "count": 1,
            "url": "/fr/tags/french-only/"
        },
        {
            "name": "Game",
            "count": 1,
            "url": "/fr/tags/game/"
        }
    ]

    # Use admin client with enabled preview mode, it should see unavailable items
    url = translate_url(reverse("lotus:tag-index"), "en")
    enable_preview(admin_client)
    response = admin_client.get(url)
    assert response.status_code == 200
    # Get tag index url for lambda user with defaut language 'en'
    url = reverse("lotus:tag-index")
    # Parse HTML response  and build a summary from found items so we can easily make
    # assertion
    dom = html_pyquery(response)
    container = dom.find("#lotus-content .tag-list-container .list.container")[0]
    tags = [
        {
            "name": item.text.strip(),
            "count": int(item.cssselect("span")[0].text.strip()),
            "url": item.get("href"),
        }
        for item in container.cssselect("a")
    ]
    assert tags == [
        {
            "name": "Game",
            "count": 2,
            "url": "/en/tags/game/"
        },
        {
            "name": "Music",
            "count": 2,
            "url": "/en/tags/music/"
        },
        {
            "name": "Not available",
            "count": 3,
            "url": "/en/tags/not-available/"
        },
        {
            "name": "Science",
            "count": 3,
            "url": "/en/tags/science/"
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_tag_view_detail(db, admin_client, client, enable_preview, settings):
    """
    Tag detail should list its related article respecting criterias and article list
    pagination should be triggered when there is enough articles.
    """
    # NOTE: A test playing with language and view requests must enforce default
    # language since LANGUAGE_CODE may be altered between two tests.
    settings.LANGUAGE_CODE = "en"

    utc = ZoneInfo("UTC")
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    science = TagFactory(name="Science", slug="science")
    sausage = TagFactory(name="Sausage", slug="sausage")
    TagFactory(name="Not used", slug="not-used")

    ArticleFactory(title="Foo", fill_tags=[science])
    ArticleFactory(title="Bar", fill_tags=[science])

    # Unavailable articles to anonymous
    ArticleFactory(
        title="France",
        fill_tags=[science],
        language="fr",
    )
    # Unavailable articles to anonymous
    ArticleFactory(
        title="Ping",
        fill_tags=[science],
        status=STATUS_DRAFT,
    )
    ArticleFactory(
        title="Pong",
        fill_tags=[science],
        private=True,
    )
    ArticleFactory(
        title="Pang",
        fill_tags=[science],
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    ArticleFactory(
        title="Nope",
        fill_tags=[sausage],
    )

    # Get tag index url for lambda user with defaut language 'en'
    url = reverse("lotus:tag-detail", kwargs={"tag": science.slug})
    # Get page HTML
    response = client.get(url)
    assert response.status_code == 200
    # Parse HTML response  and build a summary from found items so we can easily make
    # assertion
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .articles .article")
    content = []
    for item in items:
        title = item.cssselect(".title")[0].text
        content.append(title)

    assert content == ["Bar", "Foo"]

    # No pagination HTML is displayed when limit have not been reached
    pagination = dom.find("#lotus-content .articles .pagination")
    assert len(pagination) == 0

    # Admin in preview mode should be able to see every article related to the tag
    enable_preview(admin_client)
    response = admin_client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)
    items = dom.find("#lotus-content .articles .article")
    content = []
    for item in items:
        title = item.cssselect(".title")[0].text
        content.append(title)

    assert content == ["Pang", "Bar", "Foo", "Ping", "Pong"]

    # Create some other articles to trigger pagination limit
    ArticleFactory.create_batch(
        settings.LOTUS_ARTICLE_PAGINATION,
        fill_tags=[science],
    )
    response = client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)
    pagination = dom.find("#lotus-content .articles .pagination")
    assert len(pagination) == 1


def test_tag_view_autocomplete(db, admin_client, client, enable_preview, settings):
    """
    Autocomplete view should be only available for admins, returning list in JSON to
    the requests.
    """
    user = AuthorFactory()

    TagFactory(name="Science theme", slug="science")
    TagFactory(name="Sausage food", slug="sausage")
    TagFactory(name="Game theme", slug="game")
    TagFactory(name="Ping", slug="ping")
    TagFactory(name="Ping pong", slug="ping-pong")
    TagFactory(name="Music theme", slug="music")
    TagFactory(name="French theme", slug="french")
    TagFactory(name="Not available", slug="not-available")

    url = reverse("lotus:tag-autocomplete")

    # Anonymous can not reach the view
    response = client.get(url)
    assert response.status_code == 302

    # Simple logged in user can not reach the view
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 403

    # Simple get request return every tags (with possible pagination)
    response = admin_client.get(url)
    assert response.status_code == 200
    json_data = response.json()
    tags = [item["text"] for item in json_data["results"]]
    assert tags == [
        "French theme",
        "Game theme",
        "Music theme",
        "Not available",
        "Ping",
        "Ping pong",
        "Sausage food",
        "Science theme",
    ]
    assert json_data["pagination"] == {"more": False}

    # POST request is forbidden
    response = admin_client.post(url, {"q": "Ping"}, HTTP_ACCEPT="application/json")
    assert response.status_code == 400

    # Demonstrate queryset match which is basically a "startswith"
    response = admin_client.get(url, {"q": "S"}, HTTP_ACCEPT="application/json")
    assert [item["text"] for item in response.json()["results"]] == [
        "Sausage food",
        "Science theme",
    ]

    response = admin_client.get(url, {"q": "Niet"}, HTTP_ACCEPT="application/json")
    assert [item["text"] for item in response.json()["results"]] == []

    response = admin_client.get(url, {"q": "theme"}, HTTP_ACCEPT="application/json")
    assert [item["text"] for item in response.json()["results"]] == []

    response = admin_client.get(url, {"q": "Scie"}, HTTP_ACCEPT="application/json")
    assert [item["text"] for item in response.json()["results"]] == ["Science theme"]

    response = admin_client.get(url, {"q": "Ping"}, HTTP_ACCEPT="application/json")
    assert [item["text"] for item in response.json()["results"]] == [
        "Ping", "Ping pong"
    ]
