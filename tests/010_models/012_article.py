from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.urls import reverse

import pytest

from lotus.factories import ArticleFactory, CategoryFactory, multilingual_article
from lotus.models import Article


def test_basic(db):
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


def test_required_fields(db):
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


def test_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    ping = CategoryFactory(title="Ping", slug="ping")
    pong = CategoryFactory(title="Pong", slug="pong")

    article = ArticleFactory(
        title="foo",
        fill_categories=[ping, pong],
    )
    assert article.title == "foo"

    # Check related categories
    categories = article.categories.all().values(
        "title", "language"
    ).order_by("title", "language")

    assert list(categories) == [
        {"title": "Ping", "language": "en"},
        {"title": "Pong", "language": "en"},
    ]


def test_uniqueness_with_lang(db):
    """
    Article can't have the same title, slug or original on the same language.
    """
    original = ArticleFactory(title="foo", slug="bar")
    ArticleFactory(title="fiou", slug="le bar", original=original)

    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(title="foo")

    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(title="Plop", slug="bar")

    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            ArticleFactory(title="fiou", slug="le bar", original=original)


def test_multilingual_article(db):
    """
    Factory helper should create an original article with its required
    translations.
    """
    ping = CategoryFactory(title="Ping", slug="ping")
    pong = CategoryFactory(title="Pong", slug="pong")

    # Create an article with a FR and DE translations. Also try to create
    # Deutsch translations twice, but "multilingual_article" is safe on unique
    # language.
    created = multilingual_article(
        title="Cheese",
        langs=["fr", "de", "de"],
        fill_categories=[ping, pong],
        contents={
            "fr": {
                "title": "Fromage",
                "fill_categories": [ping],
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

    # Check original categories
    original_categories = created["original"].categories.all().values(
        "title", "language"
    ).order_by("title", "language")

    assert list(original_categories) == [
        {"title": "Ping", "language": "en"},
        {"title": "Pong", "language": "en"},
    ]

    # Check french translation categories
    fr_categories = created["translations"]["fr"].categories.all().values(
        "title", "language"
    ).order_by("title", "language")

    assert list(fr_categories) == [
        {"title": "Ping", "language": "en"},
    ]
