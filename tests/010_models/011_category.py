import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.urls import reverse

from lotus.factories import CategoryFactory, multilingual_category
from lotus.models import Category


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


def test_uniqueness_with_lang(db):
    """
    Category can't have the same title, slug or original on the same language.
    """
    original = CategoryFactory(title="foo", slug="bar")
    CategoryFactory(title="fiou", slug="le bar", original=original)

    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(title="foo")

    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(title="Plop", slug="bar")

    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(title="fiou", slug="le bar", original=original)


def test_multilingual_category(db):
    """
    Factory helper should create an original category with its required
    translations.
    """
    # Create a category with a FR and DE translations. Also try to create
    # Deutsch translations twice, but "multilingual_category" is safe on unique
    # language.
    created = multilingual_category(
        title="Cheese",
        langs=["fr", "de", "de"],
        contents={
            "fr": {
                "title": "Fromage",
            }
        },
    )

    # Original title is correct
    assert created["original"].title == "Cheese"

    # There is two related translations
    assert (len(created["translations"]) == 2) is True

    # Required translations have been create
    assert ("fr" in created["translations"]) is True
    assert ("de" in created["translations"]) is True

    # French translation have its own title
    assert created["translations"]["fr"].title == "Fromage"
    # Deutsch translation inherit from original title
    assert created["translations"]["de"].title == "Cheese"


def test_category_get_by_lang(db):
    """
    Demonstrate how we can get categories for original language or translations.
    """
    created_foobar = CategoryFactory(title="Foo bar", slug="foo-bar")

    created_omelette = multilingual_category(
        title="Omelette",
        langs=["fr"],
    )

    created_cheese = multilingual_category(
        title="Cheese",
        langs=["fr", "de"],
        contents={
            "fr": {
                "title": "Fromage",
            }
        },
    )

    # Get full total all languages mixed and without any filtering
    results = list(
        Category.objects.all().values(
            "title", "language"
        ).order_by("title", "language")
    )
    assert results == [
        {"title": "Cheese", "language": "de"},
        {"title": "Cheese", "language": "en"},
        {"title": "Foo bar", "language": "en"},
        {"title": "Fromage", "language": "fr"},
        {"title": "Omelette", "language": "en"},
        {"title": "Omelette", "language": "fr"}
    ]

    # Get available categories for a required language
    assert Category.objects.filter(language="en").count() == 3
    assert Category.objects.filter(language="fr").count() == 2
    assert Category.objects.filter(language="de").count() == 1

    # Get only originals
    results = list(
        Category.objects.filter(
            original__isnull=True
        ).values("title", "language").order_by("title", "language")
    )
    assert results == [
        {"title": "Cheese", "language": "en"},
        {"title": "Foo bar", "language": "en"},
        {"title": "Omelette", "language": "en"},
    ]

    # Get only translations
    results = list(
        Category.objects.filter(
            original__isnull=False
        ).values("title", "language").order_by("title", "language")
    )
    assert results == [
        {"title": "Cheese", "language": "de"},
        {"title": "Fromage", "language": "fr"},
        {"title": "Omelette", "language": "fr"}
    ]

    # Get translations from original
    assert created_foobar.category_set.all().count() == 0
    assert created_omelette["original"].category_set.all().count() == 1
    assert created_cheese["original"].category_set.all().count() == 2

