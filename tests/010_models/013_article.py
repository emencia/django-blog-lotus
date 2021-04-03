import os
import datetime

import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone
from django.urls import reverse

from lotus.factories import (
    ArticleFactory, CategoryFactory, multilingual_article,
)
from lotus.models import Article
from lotus.utils.imaging import create_image_file
from lotus.utils.tests import queryset_values
from lotus.choices import STATUS_DRAFT


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
    Factory should correctly create a new object without any errors.
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

    # Ensure no random categories or authors are created when not specifically
    # required
    article = ArticleFactory(slug="bar")
    assert article.authors.count() == 0
    assert article.categories.count() == 0


def test_article_last_update(db):
    """
    Model should auto update "last_update" value on each save.
    """
    article = ArticleFactory(
        slug="foo",
    )
    assert article.last_update is not None

    # Save date for usage after change
    last_update = article.last_update

    # Trigger save for auto update
    article.save()

    assert article.last_update > last_update


def test_article_constraints_db(db):
    """
    Article contraints should be respected at database level.
    """
    now = timezone.now()
    tomorrow = now + datetime.timedelta(days=1)

    # Get a same date from "now" but shifted from an hour,
    # default to +1 hour but if it leads to a different date (like when
    # executing tests at 23:00, date will be the next day), shift to -1 hour
    shifted_time = now + datetime.timedelta(hours=1)
    if shifted_time.date() > now.date():
        shifted_time = now - datetime.timedelta(hours=1)

    # Base original objects
    bar = ArticleFactory(
        slug="bar",
        publish_date=now.date(),
        publish_time=now.time(),
    )
    ArticleFactory(
        slug="pong",
        publish_date=now.date(),
        publish_time=now.time(),
    )

    # We can have an identical slug on the same date for a different
    # language.
    # Note than original is just a marker to define an object as a translation
    # of "original" relation object.
    ArticleFactory(
        slug="bar",
        language="fr",
        original=bar,
        publish_date=now.date(),
        publish_time=now.time(),
    )

    # But only an unique language for the same original object is allowed since
    # there can't be two translations for the same language.
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(
                slug="zap",
                language="fr",
                original=bar,
                publish_date=now.date(),
                publish_time=now.time(),
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
                publish_date=now.date(),
                publish_time=now.time(),
            )
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_article.publish_date, lotus_article.slug, "
            "lotus_article.language"
        )

    # But we can have an identical slug and language on different date
    ArticleFactory(
        slug="bar",
        publish_date=tomorrow.date(),
        publish_time=tomorrow.time(),
    )

    # Or identical slug+date+original on different language
    ArticleFactory(
        slug="bar",
        language="de",
        original=bar,
        publish_date=now.date(),
        publish_time=now.time(),
    )

    # Combination of constraints (date+slug+lang & original+lang)
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(
                slug="bar",
                language="fr",
                original=bar,
                publish_date=now.date(),
                publish_time=now.time(),
            )
        # Only the original+language constraint is returned since it raises
        # first and stop other db validation
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_article.original_id, lotus_article.language"
        )


def test_article_constraints_model(db):
    """
    Article contraints should be respected at model validation level.

    We use factory build strategy to avoid automatic creation so we can test
    "full_clean" raise a validation error (to ensure constraint is not only
    enforced at DB level)
    """
    now = timezone.now()

    # Get a same date from "now" but shifted from an hour,
    # default to +1 hour but if it leads to a different date (like when
    # executing tests at 23:00, date will be the next day), shift to -1 hour
    shifted_time = now + datetime.timedelta(hours=1)
    if shifted_time.date() > now.date():
        shifted_time = now - datetime.timedelta(hours=1)

    # Base original objects
    bar = ArticleFactory(
        slug="bar",
        publish_date=now.date(),
        publish_time=now.time(),
    )
    # A translation
    ArticleFactory(
        slug="bar",
        language="fr",
        original=bar,
    )

    # Constraint unique combo date+slug+lang
    builded = ArticleFactory.build(
        slug="bar",
        publish_date=now.date(),
        publish_time=now.time(),
    )
    with pytest.raises(ValidationError) as excinfo:
        builded.full_clean()

    assert excinfo.value.message_dict == {
        "__all__": [
            "Article with this Publication date, Slug and Language already "
            "exists."
        ],
    }

    # Constraint unique combo original+lang
    builded = ArticleFactory.build(
        slug="zap",
        language="fr",
        original=bar,
        publish_date=now.date(),
        publish_time=now.time(),
    )
    with pytest.raises(ValidationError) as excinfo:
        builded.full_clean()

    assert excinfo.value.message_dict == {
        "__all__": [
            "Article with this Original and Language already exists."
        ],
    }

    # Combination of all constraints
    builded = ArticleFactory.build(
        slug="bar",
        language="fr",
        original=bar,
        publish_date=now.date(),
        publish_time=now.time(),
    )
    with pytest.raises(ValidationError) as excinfo:
        builded.full_clean()

    assert excinfo.value.message_dict == {
        "__all__": [
            "Article with this Publication date, Slug and Language already "
            "exists.",
            "Article with this Original and Language already exists.",
        ],
    }


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


def test_article_model_file_management(db):
    """
    Article 'cover' and 'image' field file management should follow correct
    behaviors:

    * When object is deleted, its files should be delete from filesystem too;
    * When changing file from an object, its previous files (if any) should be
      deleted;
    """
    ping = ArticleFactory(
        cover=create_image_file(filename="machin.png"),
        image=create_image_file(filename="ping_image.png"),
    )
    pong = ArticleFactory(
        cover=create_image_file(filename="machin.png"),
        image=create_image_file(filename="pong_image.png"),
    )

    # Memorize some data to use after deletion
    ping_cover_path = ping.cover.path
    ping_image_path = ping.image.path
    pong_cover_path = pong.cover.path
    pong_image_path = pong.image.path

    # Delete object
    ping.delete()

    # Files are deleted along their object
    assert os.path.exists(ping_cover_path) is False
    assert os.path.exists(ping_image_path) is False
    # Paranoiac mode: other existing similar filename (as uploaded) is conserved
    # (since Django rename file with a unique hash if filename alread exist)
    assert os.path.exists(pong_cover_path) is True

    # Change object file to a new one
    pong.cover = create_image_file(filename="new_cover.png")
    pong.image = create_image_file(filename="new_image.png")
    pong.save()

    # During pre save signal, old file is removed from FS and new one is left
    # untouched
    assert os.path.exists(pong_cover_path) is False
    assert os.path.exists(pong_image_path) is False
    assert os.path.exists(pong.cover.path) is True
    assert os.path.exists(pong.image.path) is True
