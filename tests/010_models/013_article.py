import datetime
from pathlib import Path

import pytest
import pytz

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone

from lotus.choices import STATUS_DRAFT
from lotus.factories import (
    ArticleFactory, CategoryFactory, multilingual_article,
)
from lotus.models import Article
from lotus.utils.imaging import DjangoSampleImageCrafter
from lotus.utils.tests import queryset_values


# Shortcut for a shorter variable name
STATES = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES


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

    assert 1 == Article.objects.filter(title="Bar").count()
    assert "Bar" == article.title


def test_article_required_fields(db):
    """
    Basic model validation with missing required language should fail
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

    # Just a dummy article
    dummy = ArticleFactory(slug="dummy", language="fr")

    # Article with some relation
    article = ArticleFactory(
        slug="foo",
        fill_categories=[ping, pong],
        fill_related=[dummy],
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

    # Check related articles
    results = queryset_values(
        article.related.all()
    )

    assert results == [
        {"slug": "dummy", "language": "fr"},
    ]

    # Check for reverse relation
    results = queryset_values(
        dummy.relations.all()
    )

    assert results == [
        {"slug": "foo", "language": "en"},
    ]

    # Ensure 'related' is not symmetrical
    assert dummy.related.count() == 0

    # Ensure no random relations are created when not specifically
    # required from "fill_****" methods
    article = ArticleFactory(slug="bar")
    assert article.authors.count() == 0
    assert article.categories.count() == 0
    assert article.related.count() == 0


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
            "Article with this Original article and Language already exists."
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
            "Article with this Original article and Language already exists.",
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


def test_article_model_file_purge(db):
    """
    Article 'cover' and 'image' field file should follow correct behaviors:

    * When object is deleted, its files should be delete from filesystem too;
    * When changing file from an object, its previous files (if any) should be
      deleted;
    """
    crafter = DjangoSampleImageCrafter()

    ping = ArticleFactory(
        cover=crafter.create(filename="machin.png"),
        image=crafter.create(filename="ping_image.png"),
    )
    pong = ArticleFactory(
        cover=crafter.create(filename="machin.png"),
        image=crafter.create(filename="pong_image.png"),
    )

    # Memorize some data to use after deletion
    ping_cover_path = ping.cover.path
    ping_image_path = ping.image.path
    pong_cover_path = pong.cover.path
    pong_image_path = pong.image.path

    # Delete object
    ping.delete()

    # Files are deleted along their object
    assert Path(ping_cover_path).exists() is False
    assert Path(ping_image_path).exists() is False
    # Paranoiac mode: other existing similar filename (as uploaded) are conserved
    # since Django rename file with a unique hash if filename alread exist, they
    # should not be mistaken
    assert Path(pong_cover_path).exists() is True

    # Change object file to a new one
    pong.cover = crafter.create(filename="new_cover.png")
    pong.image = crafter.create(filename="new_image.png")
    pong.save()

    # During pre save signal, old file is removed from FS and new one is left
    # untouched
    assert Path(pong_cover_path).exists() is False
    assert Path(pong_image_path).exists() is False
    assert Path(pong.cover.path).exists() is True
    assert Path(pong.image.path).exists() is True


def test_article_model_get_states(db):
    """
    Object method "get_states" should return the right state names depending object
    values and publication criterias.
    """
    # Date references
    default_tz = pytz.timezone("UTC")
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 00))
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 1, 00))
    yesterday = default_tz.localize(datetime.datetime(2012, 10, 14, 10, 0))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 00))

    article_draft = ArticleFactory(
        title="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    article_pinned = ArticleFactory(
        title="pinned",
        publish_date=today.date(),
        publish_time=today.time(),
        pinned=True,
    )
    article_featured = ArticleFactory(
        title="featured",
        publish_date=today.date(),
        publish_time=today.time(),
        featured=True,
    )
    article_private = ArticleFactory(
        title="private",
        publish_date=today.date(),
        publish_time=today.time(),
        private=True,
    )
    article_yesterday = ArticleFactory(
        title="published yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    article_mixed_available = ArticleFactory(
        title="pinned, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        pinned=True,
        private=True,
    )
    article_mixed_draft = ArticleFactory(
        title="draft, pinned, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        status=STATUS_DRAFT,
        pinned=True,
        private=True,
    )

    assert article_draft.get_states(now) == [
        STATES["status_draft"]
    ]
    assert article_pinned.get_states(now) == [
        STATES["pinned"], STATES["status_available"],
    ]
    assert article_featured.get_states(now) == [
        STATES["featured"], STATES["status_available"],
    ]
    assert article_private.get_states(now) == [
        STATES["private"], STATES["status_available"],
    ]
    assert article_yesterday.get_states(now) == [
        STATES["status_available"],
    ]
    assert article_mixed_draft.get_states(now) == [
        STATES["pinned"], STATES["private"], STATES["status_draft"],
    ]
    assert article_mixed_available.get_states(now) == [
        STATES["pinned"], STATES["private"], STATES["status_available"],
        STATES["publish_end_passed"],
    ]


def test_article_model_is_published(db):
    """
    TODO:
    Object method "is_published" should return a boolean for publication state.
    """
    # Date references
    default_tz = pytz.timezone("UTC")
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 00))
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 1, 00))
    yesterday = default_tz.localize(datetime.datetime(2012, 10, 14, 10, 0))
    past_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 00))
    next_hour = default_tz.localize(datetime.datetime(2012, 10, 15, 11, 00))

    draft = ArticleFactory(
        title="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    basic = ArticleFactory(
        title="basic published",
        publish_date=today.date(),
        publish_time=today.time(),
    )
    published_yesterday = ArticleFactory(
        title="published yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    published_notyet = ArticleFactory(
        title="not yet published",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    published_passed = ArticleFactory(
        title="published but ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
    )
    published_private_passed = ArticleFactory(
        title="published, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        private=True,
    )
    draft_passed = ArticleFactory(
        title="draft and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        status=STATUS_DRAFT,
    )

    assert draft.is_published(now) is False
    assert basic.is_published(now) is True
    assert published_yesterday.is_published(now) is True
    assert published_notyet.is_published(now) is False
    assert published_passed.is_published(now) is False
    assert published_private_passed.is_published(now) is False
    assert draft_passed.is_published(now) is False
