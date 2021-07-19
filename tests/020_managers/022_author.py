import datetime
import json

import pytz
from freezegun import freeze_time

from django.utils import timezone

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, AuthorFactory, multilingual_article
from lotus.models import Author
from lotus.utils.tests import queryset_values


@freeze_time("2012-10-15 10:00:00")
def test_author_manager_active(db):
    """
    Author manager should be able to get all author which have contributed to one
    article or more with possibility to filter on language.
    """
    default_tz = pytz.timezone("UTC")

    now = timezone.now()
    tomorrow = default_tz.localize(datetime.datetime(2012, 10, 16, 10, 0))
    # Today 5min sooner to avoid shifting with pytest and factory delays
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 55))

    # Some authors
    picsou = AuthorFactory(username="picsou")
    donald = AuthorFactory(username="donald")
    flairsou = AuthorFactory(username="flairsou")

    # Some articles
    ArticleFactory(
        slug="Klondike",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou],
    )

    ArticleFactory(
        slug="DuckCity",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou, donald],
    )

    ArticleFactory(
        slug="NopeCity",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou, flairsou],
        status=STATUS_DRAFT,
    )

    ArticleFactory(
        slug="Tomorrow",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        fill_authors=[donald],
    )

    ArticleFactory(
        slug="Camembert",
        language="fr",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou, flairsou],
    )

    # Check for author which have published articles for all language
    #print()
    #print("# usernames_all:")
    q_authors_published = Author.lotus_objects.get_active()
    usernames_all = queryset_values(
        q_authors_published,
        names=["username", "articles__language"],
        orders=["username"],
    )
    #print(q_authors_published)
    #print(json.dumps(usernames_all, indent=4))
    #print("<--- SQL")
    #print(q_authors_published.query)
    #print("SQL --->")
    assert usernames_all == [
        {'username': 'donald', 'articles__language': 'en'},
        {'username': 'flairsou', 'articles__language': 'fr'},
        {'username': 'picsou', 'articles__language': 'en'},
        {'username': 'picsou', 'articles__language': 'fr'},
    ]

    # Check for author which have published articles for english only
    #print()
    #print("# usernames_en:")
    q_authors_published = Author.lotus_objects.get_active(language="en")
    usernames_en = queryset_values(
        q_authors_published,
        names=["username", "articles__language"],
        orders=["username"],
    )
    #print(q_authors_published)
    #print(json.dumps(usernames_en, indent=4))
    #print("<--- SQL")
    #print(q_authors_published.query)
    #print("SQL --->")
    assert usernames_en == [
        {"username": "donald", "articles__language": "en"},
        {"username": "picsou", "articles__language": "en"},
    ]


@freeze_time("2012-10-15 10:00:00")
def test_author_manager_published(db):
    """
    Demonstrate Article manager usage from Author "articles" relation.
    """
    default_tz = pytz.timezone("UTC")

    now = timezone.now()
    tomorrow = default_tz.localize(datetime.datetime(2012, 10, 16, 10, 0))
    # Today 5min sooner
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 55))

    # Some authors
    picsou = AuthorFactory(username="picsou")
    donald = AuthorFactory(username="donald")
    flairsou = AuthorFactory(username="flairsou")

    # Some articles
    ArticleFactory(
        slug="Klondike",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou],
    )

    ArticleFactory(
        slug="DuckCity",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou, donald],
    )

    ArticleFactory(
        slug="NopeCity",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou, flairsou],
        status=STATUS_DRAFT,
    )

    ArticleFactory(
        slug="Tomorrow",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
        fill_authors=[donald],
    )

    ArticleFactory(
        slug="Camembert",
        language="fr",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_authors=[picsou, flairsou],
    )

    # Check for published articles for each author
    all_flairsou = queryset_values(flairsou.articles.get_published())
    en_flairsou = queryset_values(flairsou.articles.get_published(language="en"))
    fr_flairsou = queryset_values(flairsou.articles.get_published(language="fr"))
    assert all_flairsou == [
        {"language": "fr", "slug": "Camembert"}
    ]
    assert en_flairsou == []
    assert fr_flairsou == [
        {"language": "fr", "slug": "Camembert"}
    ]

    all_donald = queryset_values(donald.articles.get_published())
    en_donald = queryset_values(donald.articles.get_published(language="en"))
    fr_donald = queryset_values(donald.articles.get_published(language="fr"))
    assert all_donald == [
        {"language": "en", "slug": "DuckCity"},
    ]
    assert en_donald == [
        {"language": "en", "slug": "DuckCity"},
    ]
    assert fr_donald == []

    all_picsou = queryset_values(picsou.articles.get_published())
    en_picsou = queryset_values(picsou.articles.get_published(language="en"))
    fr_picsou = queryset_values(picsou.articles.get_published(language="fr"))
    assert all_picsou == [
        {"language": "fr", "slug": "Camembert"},
        {"language": "en", "slug": "DuckCity"},
        {"language": "en", "slug": "Klondike"},
    ]
    assert en_picsou == [
        {"language": "en", "slug": "DuckCity"},
        {"language": "en", "slug": "Klondike"},
    ]
    assert fr_picsou == [
        {"language": "fr", "slug": "Camembert"},
    ]

    lang_fr_picsou = queryset_values(picsou.articles.get_for_lang(language="en"))
    assert lang_fr_picsou == [
        {"language": "en", "slug": "DuckCity"},
        {"language": "en", "slug": "Klondike"},
        {"language": "en", "slug": "NopeCity"},
    ]
