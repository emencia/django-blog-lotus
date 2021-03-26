import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.urls import reverse

from lotus.factories import CategoryFactory, multilingual_category
from lotus.models import Category

from tests.utils import queryset_values


def test_basic(settings, db):
    """
    Basic model validation with required fields should not fail.
    """
    category = Category(
        title="Foo",
        slug="foo",
    )
    category.full_clean()
    category.save()

    url = reverse("lotus:category-detail", args=[
        str(category.id)
    ])

    assert 1 == Category.objects.filter(title="Foo").count()
    assert "Foo" == category.title
    assert url == category.get_absolute_url()


def test_required_fields(db):
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


def test_creation(db):
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
    pong = CategoryFactory(
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
        title="Recipe",
        langs=["fr", "de", "de"],
        contents={
            "fr": {
                "title": "Recette",
            }
        },
    )

    # Original title is correct
    assert created["original"].title == "Recipe"

    # There is two related translations
    assert (len(created["translations"]) == 2) is True

    # Required translations have been create
    assert ("fr" in created["translations"]) is True
    assert ("de" in created["translations"]) is True

    # French translation have its own title
    assert created["translations"]["fr"].title == "Recette"
    # Deutsch translation inherit from original title
    assert created["translations"]["de"].title == "Recipe"


def test_category_get_by_lang(db):
    """
    Demonstrate how we can get categories for original language and
    translations.
    """
    created_foobar = CategoryFactory(title="Foo bar", slug="foo-bar")

    created_omelette = multilingual_category(
        title="Food",
        langs=["fr"],
    )

    created_cheese = multilingual_category(
        title="Recipe",
        langs=["fr", "de"],
        contents={
            "fr": {
                "title": "Recette",
            }
        },
    )

    # Get full total all languages mixed and without any filtering
    assert queryset_values(Category.objects.all()) == [
        {"title": "Foo bar", "language": "en"},
        {"title": "Food", "language": "en"},
        {"title": "Food", "language": "fr"},
        {"title": "Recette", "language": "fr"},
        {"title": "Recipe", "language": "de"},
        {"title": "Recipe", "language": "en"},
    ]

    # Get available categories for a required language
    assert Category.objects.filter(language="en").count() == 3
    assert Category.objects.filter(language="fr").count() == 2
    assert Category.objects.filter(language="de").count() == 1

    # Get only originals
    results = Category.objects.filter(original__isnull=True)
    assert queryset_values(results) == [
        {"title": "Foo bar", "language": "en"},
        {"title": "Food", "language": "en"},
        {"title": "Recipe", "language": "en"},
    ]

    # Get only translations
    results = Category.objects.filter(original__isnull=False)
    assert queryset_values(results) == [
        {"title": "Food", "language": "fr"},
        {"title": "Recette", "language": "fr"},
        {"title": "Recipe", "language": "de"},
    ]

    # Get translations from original
    assert created_foobar.category_set.all().count() == 0
    assert created_omelette["original"].category_set.all().count() == 1
    assert created_cheese["original"].category_set.all().count() == 2


def test_category_managers(db):
    """
    Category manager should be able to correctly filter on language.
    """
    # Simple category on default language without translations
    created_foobar = CategoryFactory(title="Foo bar")

    # Original category on different language than 'settings.LANGUAGE_CODE' and
    # with a translation for 'settings.LANGUAGE_CODE' lang.
    created_baguette = multilingual_category(
        title="Musique",
        language="fr",
        langs=["en"],
        contents={
            "en": {
                "title": "Music",
            }
        },
    )

    # A category with a french translation inheriting original title
    created_omelette = multilingual_category(
        title="Omelette",
        langs=["fr"],
    )

    # A category with french translation with its own title and deutsch
    # translation inheriting original title
    created_cheese = multilingual_category(
        title="Recipe",
        langs=["fr", "de"],
        contents={
            "fr": {
                "title": "Recette",
            }
        },
    )

    # Use default language as configured in settings
    assert queryset_values(Category.objects.get_for_lang()) == [
        {"title": "Foo bar", "language": "en"},
        {"title": "Music", "language": "en"},
        {"title": "Omelette", "language": "en"},
        {"title": "Recipe", "language": "en"},
    ]

    # For french language
    assert queryset_values(Category.objects.get_for_lang("fr")) == [
        {"title": "Musique", "language": "fr"},
        {"title": "Omelette", "language": "fr"},
        {"title": "Recette", "language": "fr"},
    ]

    # For deutsch language
    assert queryset_values(Category.objects.get_for_lang("de")) == [
        {"title": "Recipe", "language": "de"},
    ]
