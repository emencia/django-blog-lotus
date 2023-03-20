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

from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory, AuthorFactory, CategoryFactory, TagFactory, multilingual_article,
)
from lotus.utils.tests import html_pyquery


def test_tag_view_index(db, admin_client, client, enable_preview, settings):
    """
    Index view should list tags used in articles respecting publication criteria.

    TODO:
    Current assertions wrong results since the index view dont care of criterias.
    """
    # NOTE: A test playing with language and view requests must enforce default
    # language since LANGUAGE_CODE may be altered between two tests.
    settings.LANGUAGE_CODE = "en"

    SORL_CACHE_PATH = str(
        Path(settings.MEDIA_URL) / Path(sorl_settings.THUMBNAIL_PREFIX)
    )

    picsou = AuthorFactory(first_name="Picsou", last_name="McDuck")

    cat_1 = CategoryFactory(title="cat_1")

    science = TagFactory(name="Science", slug="science")
    sausage = TagFactory(name="Saucage", slug="sausage")
    game = TagFactory(name="Game", slug="game")
    music = TagFactory(name="Music", slug="music")
    niet = TagFactory(name="Niet", slug="niet")

    article_foo = ArticleFactory(
        title="Foo",
        fill_tags=[science, game, music],
    )
    article_bar = ArticleFactory(
        title="Bar",
        fill_tags=[science],
    )
    article_ping = ArticleFactory(
        title="Ping",
        fill_tags=[science, sausage],
        status=STATUS_DRAFT,
    )
    article_pong = ArticleFactory(
        title="Pong",
        fill_tags=[science, game, sausage],
        private=True,
    )
    # TODO: Add an 'article_pang' with publish date out of current date

    # Get tag index url
    url = reverse("lotus:tag-index")

    # Get page HTML
    response = client.get(url)
    assert response.status_code == 200

    # Parse HTML response to get tag items
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

    import json
    print(json.dumps(tags, indent=4))

    ## Switch user to preview mode
    #enable_preview(admin_client)

    ## Get page HTML
    #response = admin_client.get(url)
    #assert response.status_code == 200

    assert 1 == 42
