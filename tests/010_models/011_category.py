from pathlib import Path

import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction

from lotus.factories import CategoryFactory, multilingual_category
from lotus.models import Category
from lotus.utils.imaging import DjangoSampleImageCrafter
from lotus.utils.tests import queryset_values


def test_category_basic(settings, db):
    """
    Basic model validation with required fields should not fail.
    """
    category = Category(
        title="Foo",
        slug="foo",
    )
    category.full_clean()
    category.save()

    assert 1 == Category.objects.filter(title="Foo").count()
    assert "Foo" == category.title


def test_category_required_fields(db):
    """
    Basic model validation with missing required fields should fail.
    """
    category = Category(language="")

    with pytest.raises(ValidationError) as excinfo:
        category.full_clean()

    assert excinfo.value.message_dict == {
        "title": ["This field cannot be blank."],
        "slug": ["This field cannot be blank."],
        "language": ["This field cannot be blank."],
    }


def test_category_creation(db):
    """
    Factory should correctly create a new object without any errors.
    """
    category = CategoryFactory(title="foo")
    assert category.title == "foo"


def test_category_constraints(db):
    """
    Category contraints should be respected.
    """
    # Base original objects
    bar = CategoryFactory(
        slug="bar",
    )
    CategoryFactory(
        slug="pong",
    )

    # We can have an identical slug for a different language.
    # Note than original is just a marker to define an object as a translation
    # of "original" relation object.
    CategoryFactory(
        slug="bar",
        language="fr",
        original=bar,
    )

    # But not an identical slug on the same language
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(
                slug="bar",
                language="en",
            )
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_category.slug, lotus_category.language"
        )

    # And only an unique language for the same original object is allowed since
    # there can't be two translations for the same language.
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(
                slug="zap",
                language="fr",
                original=bar,
            )
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_category.original_id, lotus_category.language"
        )

    # Combination of constraints (slug+lang & original+lang)
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(
                slug="bar",
                language="fr",
                original=bar,
            )
        # This is the original+language constraint which raise first
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_category.original_id, lotus_category.language"
        )


def test_multilingual_category(db):
    """
    Factory helper should create an original category with its required
    translations.
    """
    # Create a category with a FR and DE translations. Also try to create
    # Deutsch translations twice, but "multilingual_category" is safe on unique
    # language.
    created = multilingual_category(
        slug="recipe",
        langs=["fr", "de", "de"],
        contents={
            "fr": {
                "slug": "recette",
            }
        },
    )

    # Original slug is correct
    assert created["original"].slug == "recipe"

    # There is two related translations
    assert (len(created["translations"]) == 2) is True

    # Required translations have been create
    assert ("fr" in created["translations"]) is True
    assert ("de" in created["translations"]) is True

    # French translation have its own slug
    assert created["translations"]["fr"].slug == "recette"
    # Deutsch translation inherit from original slug
    assert created["translations"]["de"].slug == "recipe"


def test_category_get_by_lang(db):
    """
    Demonstrate how we can get categories for original language and
    translations.
    """
    created_foobar = CategoryFactory(slug="foobar")

    created_omelette = multilingual_category(
        slug="food",
        langs=["fr"],
    )

    created_cheese = multilingual_category(
        slug="recipe",
        langs=["fr", "de"],
        contents={
            "fr": {
                "slug": "recette",
            }
        },
    )

    # Get full total all languages mixed and without any filtering
    assert queryset_values(Category.objects.all()) == [
        {"slug": "foobar", "language": "en"},
        {"slug": "food", "language": "en"},
        {"slug": "food", "language": "fr"},
        {"slug": "recette", "language": "fr"},
        {"slug": "recipe", "language": "de"},
        {"slug": "recipe", "language": "en"},
    ]

    # Get available categories for a required language
    assert Category.objects.filter(language="en").count() == 3
    assert Category.objects.filter(language="fr").count() == 2
    assert Category.objects.filter(language="de").count() == 1

    # Get only originals
    results = Category.objects.filter(original__isnull=True)
    assert queryset_values(results) == [
        {"slug": "foobar", "language": "en"},
        {"slug": "food", "language": "en"},
        {"slug": "recipe", "language": "en"},
    ]

    # Get only translations
    results = Category.objects.filter(original__isnull=False)
    assert queryset_values(results) == [
        {"slug": "food", "language": "fr"},
        {"slug": "recette", "language": "fr"},
        {"slug": "recipe", "language": "de"},
    ]

    # Get translations from original
    assert created_foobar.category_set.all().count() == 0
    assert created_omelette["original"].category_set.all().count() == 1
    assert created_cheese["original"].category_set.all().count() == 2


def test_category_model_file_purge(db):
    """
    Category 'cover' field file should follow correct behaviors:

    * When object is deleted, its files should be delete from filesystem too;
    * When changing file from an object, its previous files (if any) should be
      deleted;
    """
    crafter = DjangoSampleImageCrafter()

    ping = CategoryFactory(
        cover=crafter.create(filename="machin.png")
    )
    pong = CategoryFactory(
        cover=crafter.create(filename="machin.png")
    )

    # Memorize some data to use after deletion
    ping_path = ping.cover.path
    pong_path = pong.cover.path

    # Delete object
    ping.delete()

    # File is deleted along its object
    assert Path(ping_path).exists() is False
    # Paranoiac mode: other existing similar filename (as uploaded) are conserved
    # since Django rename file with a unique hash if filename alread exist, they
    # should not be mistaken
    assert Path(pong_path).exists() is True

    # Change object file to a new one
    pong.cover = crafter.create(filename="new.png")
    pong.save()

    # During pre save signal, old file is removed from FS and new one is left
    # untouched
    assert Path(pong_path).exists() is False
    assert Path(pong.cover.path).exists() is True
