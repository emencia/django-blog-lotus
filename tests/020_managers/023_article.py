import datetime

import pytest
import pytz
from freezegun import freeze_time

from django.utils import timezone

from lotus.factories import ArticleFactory, multilingual_article
from lotus.models import Article
from lotus.utils.tests import queryset_values
from lotus.choices import STATUS_DRAFT


@freeze_time("2012-10-15 10:00:00")
def test_article_managers(db):
    """
    Article manager should be able to correctly filter on language and
    publication.
    """
    default_tz = pytz.timezone("UTC")

    # Craft dates
    yesterday = default_tz.localize(datetime.datetime(2012, 10, 14, 10, 0))
    tomorrow = default_tz.localize(datetime.datetime(2012, 10, 16, 10, 0))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 00))
    next_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 11, 00))
    # Today 5min sooner to avoid shifting with pytest and factory delays
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 55))

    # Single language only
    common_kwargs = {
        "publish_date": today.date(),
        "publish_time": today.time(),
    }
    ArticleFactory(slug="english", language="en", **common_kwargs)
    ArticleFactory(slug="french", language="fr", **common_kwargs)
    ArticleFactory(slug="deutsch", language="de", **common_kwargs)

    # Explicitely non published
    ArticleFactory(slug="niet", status=STATUS_DRAFT, **common_kwargs)

    # English and French
    multilingual_article(
        slug="banana",
        langs=["fr"],
        publish_date=today.date(),
        publish_time=today.time(),
    )

    # English and Deutsch translation
    multilingual_article(
        slug="burger",
        langs=["de"],
        publish_date=today.date(),
        publish_time=today.time(),
    )

    # Original Deutsch and French translation
    multilingual_article(
        slug="wurst",
        language="de",
        langs=["fr"],
        publish_date=today.date(),
        publish_time=today.time(),
    )

    # All languages and available for publication
    multilingual_article(
        slug="cheese",
        langs=["fr", "de"],
        publish_date=today.date(),
        publish_time=today.time(),
    )
    multilingual_article(
        slug="yesterday",
        langs=["fr", "de"],
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    # All lang and publish end later, still available for publication
    multilingual_article(
        slug="shortlife-to-tomorrow",
        langs=["fr", "de"],
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=tomorrow,
    )
    multilingual_article(
        slug="shortlife-to-nexthour",
        langs=["fr", "de"],
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=next_hour,
    )
    # All lang but not available for publication
    multilingual_article(
        slug="tomorrow",
        langs=["fr", "de"],
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )
    multilingual_article(
        slug="invalid-yesterday",
        langs=["fr", "de"],
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=yesterday,
    )
    multilingual_article(
        slug="will-be-next-hour",
        langs=["fr", "de"],
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )

    # Check all english articles
    assert Article.objects.get_for_lang().count() == 11

    # Check all french articles
    assert Article.objects.get_for_lang("fr").count() == 10

    # Check all french articles
    assert Article.objects.get_for_lang("de").count() == 10

    # Check all published
    assert Article.objects.get_published().count() == 21

    # Check all unpublished
    assert Article.objects.get_unpublished().count() == 10

    # Check all english published
    q_en_published = Article.objects.get_for_lang().get_published()
    assert queryset_values(q_en_published) == [
        {"slug": "banana", "language": "en"},
        {"slug": "burger", "language": "en"},
        {"slug": "cheese", "language": "en"},
        {"slug": "english", "language": "en"},
        {"slug": "shortlife-to-nexthour", "language": "en"},
        {"slug": "shortlife-to-tomorrow", "language": "en"},
        {"slug": "yesterday", "language": "en"},
    ]

    # Check all french published
    q_fr_published = Article.objects.get_for_lang("fr").get_published()
    assert queryset_values(q_fr_published) == [
        {"slug": "banana", "language": "fr"},
        {"slug": "cheese", "language": "fr"},
        {"slug": "french", "language": "fr"},
        {"slug": "shortlife-to-nexthour", "language": "fr"},
        {"slug": "shortlife-to-tomorrow", "language": "fr"},
        {"slug": "wurst", "language": "fr"},
        {"slug": "yesterday", "language": "fr"},
    ]

    # Check all deutsch published
    q_de_published = Article.objects.get_for_lang("de").get_published()
    assert queryset_values(q_de_published) == [
        {"slug": "burger", "language": "de"},
        {"slug": "cheese", "language": "de"},
        {"slug": "deutsch", "language": "de"},
        {"slug": "shortlife-to-nexthour", "language": "de"},
        {"slug": "shortlife-to-tomorrow", "language": "de"},
        {"slug": "wurst", "language": "de"},
        {"slug": "yesterday", "language": "de"},
    ]


#@pytest.mark.xfail(reason="ongoing to resolve issue #22")
def test_article_managers_bug(db):
    """
    TODO
        There is a bug causing no results even there are eligible articles.

        This is because of divided publish date and time, see
        "BasePublishedQuerySet.get_published".

        Why is publish date and time instead of datetime ? Because date is used in
        constraint at DB level for unique date with unique slug. We couldn't do it
        with a single datetime field. And we cannot make a constraint for an unique
        datetime with unique slug, because detail URLs does not include time, only date
        so we need to have multiple dates the same slug.

        Either we move back to a datetime field, but constraint will have to be removed
        and done at model level (in Model.clean) and ensure this soft constraint is
        correctly supported everywhere.

        Or we find a way to match correct datetime frame in lookups with divided date
        and time fields.
    """
    default_tz = pytz.timezone("UTC")

    # Craft dates
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 0))
    yesterday = default_tz.localize(datetime.datetime(2012, 10, 14, 10, 0))
    tomorrow = default_tz.localize(datetime.datetime(2012, 10, 16, 10, 0))
    midnight = default_tz.localize(datetime.datetime(2012, 10, 15, 0, 0))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 0))
    sooner = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 55))
    next_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 11, 0))
    next_year = default_tz.localize(datetime.datetime(2013, 10, 15, 10, 0))

    ArticleFactory(slug="yesterday", publish_date=yesterday.date(), publish_time=yesterday.time())
    ArticleFactory(slug="tomorrow", publish_date=tomorrow.date(), publish_time=tomorrow.time())
    ArticleFactory(slug="midnight", publish_date=midnight.date(), publish_time=midnight.time())
    ArticleFactory(slug="past_hour", publish_date=past_hour.date(), publish_time=past_hour.time())
    ArticleFactory(slug="sooner", publish_date=sooner.date(), publish_time=sooner.time())
    ArticleFactory(slug="next_hour", publish_date=next_hour.date(), publish_time=next_hour.time())
    ArticleFactory(slug="next_year", publish_date=next_year.date(), publish_time=next_year.time())

    print()
    print("=== Automatic now")
    results = Article.objects.get_for_lang().get_published()
    autonow_items = [item.slug for item in results]
    print(autonow_items)

    print()
    print("=== sooner")
    results = Article.objects.get_for_lang().get_published(target_date=sooner)
    sooner_items = [item.slug for item in results]
    print(sooner_items)

    # Here is reproduction of expected bug. Publish dates is below targeted date but
    # publish times are always bigger than targeted time.
    print()
    print("=== forged five days in futur")
    results = Article.objects.get_for_lang().get_published(
        target_date=default_tz.localize(datetime.datetime(2012, 10, 20, 0, 0))
    )
    futur_items = [item.slug for item in results]
    print(futur_items)

    assert sorted(autonow_items) == [
        "midnight", "past_hour", "sooner", "yesterday",
    ]
    assert sorted(forgednow_items) == [
        "midnight", "past_hour", "sooner", "yesterday",
    ]
    assert sorted(sooner_items) == [
        "midnight", "past_hour", "sooner",
    ]
    assert sorted(futur_items) == [
        "midnight", "next_hour", "past_hour", "sooner", "tomorrow", "yesterday",
    ]

    assert 1 == 42


#@pytest.mark.xfail(reason="ongoing to resolve issue #22")
def test_date_n_time_lookups(db):
    """
    TODO
        A more basic test for R&D to find a way of matching correctly a datetime frame
        against a composition of a date and a time fields.
    """
    default_tz = pytz.timezone("UTC")

    now = timezone.now()
    now_forged = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 0))
    yesterday = default_tz.localize(datetime.datetime(2012, 10, 14, 10, 0))
    tomorrow = default_tz.localize(datetime.datetime(2012, 10, 16, 10, 0))
    midnight = default_tz.localize(datetime.datetime(2012, 10, 15, 0, 0))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 0))
    sooner = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 55))
    next_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 11, 0))
    next_year = default_tz.localize(datetime.datetime(2013, 10, 15, 10, 0))

    target = default_tz.localize(datetime.datetime(2012, 10, 20, 0, 0))

    assert 1 == 42
