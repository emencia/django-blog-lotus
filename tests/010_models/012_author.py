import datetime

import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone

from lotus.factories import ArticleFactory, AuthorFactory
from lotus.models import Author

from tests.utils import queryset_values


def test_author_basic(settings, db):
    """
    Basic model validation with required fields should not fail.
    """
    author = Author(
        username="foobar",
        password="secret",
    )
    author.full_clean()
    author.save()

    assert 1 == Author.objects.filter(username="foobar").count()
    assert "foobar" == author.username


def test_author_required_fields(db):
    """
    Basic model validation with missing required fields should fail.
    """
    author = Author()

    with pytest.raises(ValidationError) as excinfo:
        author.full_clean()

    assert excinfo.value.message_dict == {
        "username": ["This field cannot be blank."],
        "password": ["This field cannot be blank."],
    }


def test_author_creation(db):
    """
    Factory should correctly create a new object without any errors.
    """
    author = AuthorFactory(username="foobar")
    assert author.username == "foobar"


def test_author_manager(db):
    """
    Author manager should be able to get all author which have published
    articles and Author method "published_articles" should return all published
    articles for an Author object.
    """
    now = timezone.now()
    tomorrow = now + datetime.timedelta(days=1)
    # Today 5min sooner to avoid shifting with pytest and factory delays
    today = now - datetime.timedelta(minutes=5)

    # Some authors
    picsou = AuthorFactory(username="picsou")
    donald = AuthorFactory(username="donald")
    flairsou = AuthorFactory(username="flairsou")

    # Some articles
    ArticleFactory(
        slug="Klondike",
        publish_start=today,
        fill_authors=[picsou],
    )

    ArticleFactory(
        slug="DuckCity",
        publish_start=today,
        fill_authors=[picsou, donald],
    )

    ArticleFactory(
        slug="Tomorrow",
        publish_start=tomorrow,
        fill_authors=[donald],
    )

    # Check for author which have published articles
    q_authors_published = Author.lotus_objects.get_published()
    data = queryset_values(q_authors_published, names=["username"],
                           orders=["username"])

    assert data == [{"username": "donald"}, {"username": "picsou"}]

    # Check for published articles for each author
    assert queryset_values(flairsou.articles.get_published()) == []

    assert queryset_values(donald.articles.get_published()) == [
        {"language": "en", "slug": "DuckCity"},
    ]

    assert queryset_values(picsou.articles.get_published()) == [
        {"language": "en", "slug": "DuckCity"},
        {"language": "en", "slug": "Klondike"},
    ]
