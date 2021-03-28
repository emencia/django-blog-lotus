import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone
from django.urls import reverse

import pytest

from lotus.factories import (
    ArticleFactory, CategoryFactory, multilingual_article,
)
from lotus.models import Article

from tests.utils import queryset_values


def test_article_basic(db):
    """
    Basic model saving with required fields should not fail
    """
    article = Article(
        title="Bar",
        slug="bar",
    )
    article.full_clean()
    article.save()

    url = reverse("lotus:article-detail", args=[
        str(article.id)
    ])

    assert 1 == Article.objects.filter(title="Bar").count()
    assert "Bar" == article.title
    assert url == article.get_absolute_url()


def test_article_required_fields(db):
    """
    Basic model validation with missing required files should fail
    """
    article = Article(language="")

    with pytest.raises(ValidationError) as excinfo:
        article.full_clean()

    assert excinfo.value.message_dict == {
        "title": ["This field cannot be blank."],
        "slug": ["This field cannot be blank."],
        "language": ["This field cannot be blank."],
    }


def test_article_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    ping = CategoryFactory(slug="ping")
    pong = CategoryFactory(slug="pong")

    article = ArticleFactory(
        slug="foo",
        fill_categories=[ping, pong],
    )
    assert article.slug == "foo"

    # Check related categories
    results = queryset_values(
        article.categories.all()
    )

    assert results == [
        {"slug": "ping", "language": "en"},
        {"slug": "pong", "language": "en"},
    ]


def test_article_constraints(db):
    """
    Article contraints should be respected.
    """
    now = timezone.now()
    later = now + datetime.timedelta(hours=1)

    # Base original objects
    bar = ArticleFactory(
        slug="bar",
        publish_start=now,
    )
    ArticleFactory(
        slug="pong",
        publish_start=now,
    )

    # We can have an identical slug on the same date for a different
    # language.
    # Note than original is just a marker to define an object as a translation
    # of "original" relation object.
    ArticleFactory(
        slug="bar",
        language="fr",
        original=bar,
        publish_start=now,
    )

    # But only an unique language for the same original object is allowed since
    # there can't be two translations for the same language.
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(
                slug="zap",
                language="fr",
                original=bar,
                publish_start=now,
            )
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_article.original_id, lotus_article.language"
        )

    # Can't have an identical slug and language on the same date
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(
                slug="bar",
                publish_start=now,
            )
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_article.publish_start, lotus_article.slug, "
            "lotus_article.language"
        )

    # But we can have an identical slug and language on different date
    ArticleFactory(
        slug="bar",
        publish_start=later,
    )

    # Or identical slug+date+original on different language
    ArticleFactory(
        slug="bar",
        language="de",
        original=bar,
        publish_start=now,
    )

    # Combination of constraints (date+slug+lang & original+lang)
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(
                slug="bar",
                language="fr",
                original=bar,
                publish_start=now,
            )
        # This is the original+language constraint which raise first
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_article.original_id, lotus_article.language"
        )


def test_multilingual_article(db):
    """
    Factory helper should create an original article with its required
    translations.
    """
    ping = CategoryFactory(slug="ping")
    pong = CategoryFactory(slug="pong")

    # Create an article with a FR and DE translations. Also try to create
    # Deutsch translations twice, but "multilingual_article" is safe on unique
    # language.
    created = multilingual_article(
        slug="cheese",
        langs=["fr", "de", "de"],
        fill_categories=[ping, pong],
        contents={
            "fr": {
                "slug": "fromage",
                "fill_categories": [ping],
            }
        },
    )

    # Original slug is correct
    assert created["original"].slug == "cheese"

    # There is two related translations
    assert (len(created["translations"]) == 2) is True

    # Required translations have been create
    assert ("fr" in created["translations"]) is True
    assert ("de" in created["translations"]) is True

    # French translation have its own slug
    assert created["translations"]["fr"].slug == "fromage"
    # deutsch translation inherit from original slug
    assert created["translations"]["de"].slug == "cheese"

    # Check original categories
    original_categories = queryset_values(
        created["original"].categories.all()
    )

    assert original_categories == [
        {"slug": "ping", "language": "en"},
        {"slug": "pong", "language": "en"},
    ]

    # Check french translation categories
    fr_categories = queryset_values(
        created["translations"]["fr"].categories.all()
    )

    assert fr_categories == [
        {"slug": "ping", "language": "en"},
    ]


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
    ArticleFactory(slug="english", language="en", publish_start=today)
    ArticleFactory(slug="french", language="fr", publish_start=today)
    ArticleFactory(slug="deutsch", language="de", publish_start=today)

    # English and French
    multilingual_article(
        slug="banana",
        langs=["fr"],
        publish_start=today,
    )

    # English and Deutsch translation
    multilingual_article(
        slug="burger",
        langs=["de"],
        publish_start=today,
    )

    # Original Deutsch and French translation
    multilingual_article(
        slug="wurst",
        language="de",
        langs=["fr"],
        publish_start=today,
    )

    # All languages and available for publication
    multilingual_article(
        slug="cheese",
        langs=["fr", "de"],
        publish_start=today,
    )
    multilingual_article(
        slug="yesterday",
        langs=["fr", "de"],
        publish_start=yesterday,
    )
    # All lang and publish ends tomorrow, still available for publication
    multilingual_article(
        slug="shortlife-today",
        langs=["fr", "de"],
        publish_start=today,
        publish_end=tomorrow,
    )
    # All lang but not available for publication
    multilingual_article(
        slug="tomorrow",
        langs=["fr", "de"],
        publish_start=tomorrow,
    )
    multilingual_article(
        slug="invalid-yesterday",
        langs=["fr", "de"],
        publish_start=today,
        publish_end=yesterday,
    )

    # Check all english articles
    assert Article.objects.get_for_lang().count() == 8

    # Check all french articles
    assert Article.objects.get_for_lang("fr").count() == 8

    # Check all french articles
    assert Article.objects.get_for_lang("de").count() == 8

    # Check all published
    assert Article.objects.get_published().count() == 18

    # Check all unpublished
    assert Article.objects.get_unpublished().count() == 6

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
