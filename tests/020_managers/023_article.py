import datetime

from django.utils import timezone

from lotus.factories import ArticleFactory, multilingual_article
from lotus.models import Article
from lotus.utils.tests import queryset_values
from lotus.choices import STATUS_DRAFT


def test_article_managers(db):
    """
    Article manager should be able to correctly filter on language and
    publication.
    """
    now = timezone.now()
    yesterday = now - datetime.timedelta(days=1)
    tomorrow = now + datetime.timedelta(days=1)
    # Today 5min sooner to avoid shifting with pytest and factory delays
    today = now - datetime.timedelta(minutes=5)

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
    # All lang and publish ends tomorrow, still available for publication
    multilingual_article(
        slug="shortlife-today",
        langs=["fr", "de"],
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=tomorrow,
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

    # Check all english articles
    assert Article.objects.get_for_lang().count() == 9

    # Check all french articles
    assert Article.objects.get_for_lang("fr").count() == 8

    # Check all french articles
    assert Article.objects.get_for_lang("de").count() == 8

    # Check all published
    assert Article.objects.get_published().count() == 18

    # Check all unpublished
    assert Article.objects.get_unpublished().count() == 7

    # Check all english published
    q_en_published = Article.objects.get_for_lang().get_published()
    assert queryset_values(q_en_published) == [
        {"slug": "banana", "language": "en"},
        {"slug": "burger", "language": "en"},
        {"slug": "cheese", "language": "en"},
        {"slug": "english", "language": "en"},
        {"slug": "shortlife-today", "language": "en"},
        {"slug": "yesterday", "language": "en"},
    ]

    # Check all french published
    q_fr_published = Article.objects.get_for_lang("fr").get_published()
    assert queryset_values(q_fr_published) == [
        {"slug": "banana", "language": "fr"},
        {"slug": "cheese", "language": "fr"},
        {"slug": "french", "language": "fr"},
        {"slug": "shortlife-today", "language": "fr"},
        {"slug": "wurst", "language": "fr"},
        {"slug": "yesterday", "language": "fr"},
    ]

    # Check all deutsch published
    q_de_published = Article.objects.get_for_lang("de").get_published()
    assert queryset_values(q_de_published) == [
        {"slug": "burger", "language": "de"},
        {"slug": "cheese", "language": "de"},
        {"slug": "deutsch", "language": "de"},
        {"slug": "shortlife-today", "language": "de"},
        {"slug": "wurst", "language": "de"},
        {"slug": "yesterday", "language": "de"},
    ]
