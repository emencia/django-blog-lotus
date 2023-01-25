import datetime

from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory, CategoryFactory, multilingual_article,
)
from lotus.models import Article
from lotus.utils.tests import queryset_values


@freeze_time("2012-10-15 10:00:00")
def test_article_managers(db):
    """
    Article manager should be able to correctly filter on language and
    publication.
    """
    utc = ZoneInfo("UTC")

    # Craft dates
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)
    # Today 5min sooner
    today = datetime.datetime(2012, 10, 15, 9, 55).replace(tzinfo=utc)

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

    # Check all articles for default language
    assert Article.objects.count() == 31

    # Check articles for each language
    assert Article.objects.get_for_lang("en").count() == 11
    assert Article.objects.get_for_lang("fr").count() == 10
    assert Article.objects.get_for_lang("de").count() == 10

    # Check all published
    assert Article.objects.get_published().count() == 21

    # Check all unpublished
    assert Article.objects.get_unpublished().count() == 10
    # Check all english published
    q_en_published = Article.objects.get_published(language="en")
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
    q_fr_published = Article.objects.get_published(language="fr")
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
    q_de_published = Article.objects.get_published(language="de")
    assert queryset_values(q_de_published) == [
        {"slug": "burger", "language": "de"},
        {"slug": "cheese", "language": "de"},
        {"slug": "deutsch", "language": "de"},
        {"slug": "shortlife-to-nexthour", "language": "de"},
        {"slug": "shortlife-to-tomorrow", "language": "de"},
        {"slug": "wurst", "language": "de"},
        {"slug": "yesterday", "language": "de"},
    ]


@freeze_time("2012-10-15 10:00:00")
def test_article_managers_publication_time(db):
    """
    This test ensure manager behavior to get published and unpublished article following
    publication criteria (status, publish start and publish end) and especially about
    "publish_time" correct usage and results.

    This is required since publish start datetime is modelized with distinct field for
    date and time (which is required to have correct constraint) and so require a more
    complex lookup than with a simple datetime field.
    """
    utc = ZoneInfo("UTC")

    # Craft dates
    forged_now = datetime.datetime(2012, 10, 15, 10, 0).replace(tzinfo=utc)
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)
    midnight = datetime.datetime(2012, 10, 15, 0, 0).replace(tzinfo=utc)
    past_hour = datetime.datetime(2012, 10, 15, 9, 0).replace(tzinfo=utc)
    sooner = datetime.datetime(2012, 10, 15, 9, 55).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 0).replace(tzinfo=utc)
    next_year = datetime.datetime(2013, 10, 15, 10, 0).replace(tzinfo=utc)

    ArticleFactory(
        slug="yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time()
    )
    ArticleFactory(
        slug="tomorrow",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time()
    )
    ArticleFactory(
        slug="midnight",
        publish_date=midnight.date(),
        publish_time=midnight.time()
    )
    ArticleFactory(
        slug="past_hour",
        publish_date=past_hour.date(),
        publish_time=past_hour.time()
    )
    ArticleFactory(
        slug="sooner",
        publish_date=sooner.date(),
        publish_time=sooner.time()
    )
    ArticleFactory(
        slug="next_hour",
        publish_date=next_hour.date(),
        publish_time=next_hour.time()
    )
    ArticleFactory(
        slug="next_year",
        publish_date=next_year.date(),
        publish_time=next_year.time()
    )

    results = Article.objects.get_published(language="en")
    autonow_items = [item.slug for item in results]

    results = Article.objects.get_published(target_date=forged_now, language="en")
    forgednow_items = [item.slug for item in results]

    results = Article.objects.get_published(target_date=sooner, language="en")
    sooner_items = [item.slug for item in results]

    results = Article.objects.get_published(target_date=tomorrow, language="en")
    tomorrow_items = [item.slug for item in results]

    results = Article.objects.get_published(target_date=yesterday, language="en")
    yesterday_items = [item.slug for item in results]

    # Here is reproduction of expected bug. Publish dates is below targeted date but
    # publish times are always bigger than targeted time.
    results = Article.objects.get_published(
        target_date=datetime.datetime(2012, 10, 20, 0, 0).replace(tzinfo=utc),
        language="en",
    )
    futur_items = [item.slug for item in results]

    assert sorted(autonow_items) == [
        "midnight", "past_hour", "sooner", "yesterday",
    ]
    assert sorted(forgednow_items) == [
        "midnight", "past_hour", "sooner", "yesterday",
    ]
    assert sorted(sooner_items) == [
        "midnight", "past_hour", "sooner", "yesterday",
    ]
    assert sorted(yesterday_items) == [
        "yesterday",
    ]
    assert sorted(tomorrow_items) == [
        "midnight", "next_hour", "past_hour", "sooner", "tomorrow", "yesterday",
    ]
    assert sorted(futur_items) == [
        "midnight", "next_hour", "past_hour", "sooner", "tomorrow", "yesterday",
    ]


def test_article_managers_get_siblings(db):
    """
    Manager method "get_siblings" should return all siblings article translations
    respecting publication criterias if needed.
    """
    utc = ZoneInfo("UTC")
    now = datetime.datetime(2012, 10, 15, 10, 00).replace(tzinfo=utc)
    today = datetime.datetime(2012, 10, 15, 9, 55).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    ping = CategoryFactory(slug="ping")

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

    # Create meat articles with FR and DE translations, but DE is not published
    created_beef = multilingual_article(
        title="Beef",
        slug="beef",
        langs=["fr", "de"],
        fill_categories=[ping],
        contents={
            "fr": {
                "title": "Boeuf",
                "slug": "boeuf",
                "fill_categories": [ping],
            },
            "de": {
                "title": "Rindfleisch",
                "slug": "rindfleisch",
                "fill_categories": [ping],
                "status": STATUS_DRAFT,
            }
        },
    )

    # Create fruit articles with FR and DE translations, but FR is not yet published
    # (scheduled for next day)
    created_pineapple = multilingual_article(
        title="Pineapple",
        slug="pineapple",
        langs=["fr", "de"],
        fill_categories=[ping],
        publish_date=today.date(),
        publish_time=today.time(),
        contents={
            "fr": {
                "title": "Ananas",
                "slug": "ananas",
                "fill_categories": [ping],
            },
            "de": {
                "title": "Die Ananas",
                "slug": "die-ananas",
                "fill_categories": [ping],
                "publish_date": tomorrow.date(),
                "publish_time": tomorrow.time(),
            }
        },
    )

    # Get all siblings slugs ordered
    cheese_siblings = Article.objects.get_siblings(
        source=created_cheese["original"]
    ).values_list('slug', flat=True).order_by("slug")

    fromage_siblings = Article.objects.get_siblings(
        source=created_cheese["translations"]["fr"]
    ).values_list('slug', flat=True).order_by("slug")

    kase_siblings = Article.objects.get_siblings(
        source=created_cheese["translations"]["de"]
    ).values_list('slug', flat=True).order_by("slug")

    assert list(cheese_siblings) == [
        "fromage", "kase",
    ]
    assert list(fromage_siblings) == [
        "cheese", "kase",
    ]
    assert list(kase_siblings) == [
        "cheese", "fromage",
    ]

    # Get published ordered slugs without care of date pub
    beef_siblings = Article.objects.get_siblings(
        source=created_beef["original"]
    ).get_published().values_list('slug', flat=True).order_by("slug")

    boeuf_siblings = Article.objects.get_siblings(
        source=created_beef["translations"]["fr"]
    ).get_published().values_list('slug', flat=True).order_by("slug")

    rindfleisch_siblings = Article.objects.get_siblings(
        source=created_beef["translations"]["de"]
    ).get_published().values_list('slug', flat=True).order_by("slug")

    assert list(beef_siblings) == [
        "boeuf",
    ]
    assert list(boeuf_siblings) == [
        "beef",
    ]
    assert list(rindfleisch_siblings) == [
        "beef", "boeuf",
    ]

    # Get published ordered slugs for given date
    pineapple_siblings = Article.objects.get_siblings(
        source=created_pineapple["original"]
    ).get_published(target_date=now).values_list('slug', flat=True).order_by("slug")

    ananas_siblings = Article.objects.get_siblings(
        source=created_pineapple["translations"]["fr"]
    ).get_published(target_date=now).values_list('slug', flat=True).order_by("slug")

    dieananas_siblings = Article.objects.get_siblings(
        source=created_pineapple["translations"]["de"]
    ).get_published(target_date=now).values_list('slug', flat=True).order_by("slug")

    assert list(pineapple_siblings) == [
        "ananas",
    ]
    assert list(ananas_siblings) == [
        "pineapple",
    ]
    assert list(dieananas_siblings) == [
        "ananas", "pineapple",
    ]
