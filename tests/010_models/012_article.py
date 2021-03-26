import datetime

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone
from django.urls import reverse

import pytest

from lotus.factories import (
    ArticleFactory, CategoryFactory,
    multilingual_article, multilingual_category,
)
from lotus.models import Article

from tests.utils import queryset_values


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
    results = queryset_values(
        article.categories.all()
    )

    assert results == [
        {"title": "Ping", "language": "en"},
        {"title": "Pong", "language": "en"},
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
    pong = ArticleFactory(
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
    original_categories = queryset_values(
        created["original"].categories.all()
    )

    assert original_categories == [
        {"title": "Ping", "language": "en"},
        {"title": "Pong", "language": "en"},
    ]

    # Check french translation categories
    fr_categories = queryset_values(
        created["translations"]["fr"].categories.all()
    )

    assert fr_categories == [
        {"title": "Ping", "language": "en"},
    ]


#def test_category_managers(db):
    #"""
    #Article manager should be able to correctly filter on language and
    #publication.
    #
    # TODO
    #"""
    #category_baguette = multilingual_category(
        #title="Baguette",
        #language="fr",
        #langs=["en", "de"],
        #contents={
            #"en": {
                #"title": "French stick",
            #},
            #"de": {
                #"title": "Stangenbrot",
            #},
        #},
    #)
    #category_omelette = multilingual_category(
        #title="Omelette",
        #langs=["fr", "de"],
    #)
    #category_foobar = multilingual_category(
        #title="Foo bar",
        #langs=["fr", "de"],
    #)

    ## Simple category on default language without translations
    #created_foobar = CategoryFactory(title="Foo bar")

    ## Original category on different language than 'settings.LANGUAGE_CODE' and
    ## with a translation for 'settings.LANGUAGE_CODE' lang.
    #created_baguette = multilingual_article(
        #title="Baguette",
        #language="fr",
        #langs=["en"],
        #contents={
            #"en": {
                #"title": "French stick",
            #}
        #},
    #)

    ## A category with a french translation inheriting original title
    #created_omelette = multilingual_article(
        #title="Omelette",
        #langs=["fr"],
    #)

    ## A category with french translation with its own title and deutsch
    ## translation inheriting original title
    #created_cheese = multilingual_article(
        #title="Cheese",
        #langs=["fr", "de"],
        #contents={
            #"fr": {
                #"title": "Fromage",
            #}
        #},
    #)

    #assert queryset_values(Category.objects.get_for_lang()) == [
        #{"title": "Cheese", "language": "en"},
        #{"title": "Foo bar", "language": "en"},
        #{"title": "French stick", "language": "en"},
        #{"title": "Omelette", "language": "en"}
    #]

    #assert queryset_values(Category.objects.get_for_lang("fr")) == [
        #{"title": "Baguette", "language": "fr"},
        #{"title": "Fromage", "language": "fr"},
        #{"title": "Omelette", "language": "fr"}
    #]

    #assert queryset_values(Category.objects.get_for_lang("de")) == [
        #{"title": "Cheese", "language": "de"}
    #]
