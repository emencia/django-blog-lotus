import json
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

from django.urls import translate_url, reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory, TagFactory, multilingual_article,
)
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
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)
    past_hour = datetime.datetime(2012, 10, 15, 9, 00).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")

    cat_1 = CategoryFactory(title="cat_1")

    science = TagFactory(name="Science", slug="science")
    sausage = TagFactory(name="Sausage", slug="sausage")
    game = TagFactory(name="Game", slug="game")
    music = TagFactory(name="Music", slug="music")
    french_only = TagFactory(name="French only", slug="french-only")
    not_available = TagFactory(name="Not available", slug="not-available")
    TagFactory(name="Not used", slug="not-used")

    article_foo = ArticleFactory(
        title="Foo",
        fill_tags=[science, game, music],
    )
    article_bar = ArticleFactory(
        title="Bar",
        fill_tags=[science],
    )
    article_france = ArticleFactory(
        title="France",
        fill_tags=[game, french_only],
        language="fr",
    )
    article_ping = ArticleFactory(
        title="Ping",
        fill_tags=[science, not_available],
        status=STATUS_DRAFT,
    )
    article_pong = ArticleFactory(
        title="Pong",
        fill_tags=[game, not_available],
        private=True,
    )
    article_pang = ArticleFactory(
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
    # print()
    # print(json.dumps(tags, indent=4))
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
