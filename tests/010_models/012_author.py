import pytest

from django.core.exceptions import ValidationError

from lotus.factories import AuthorFactory
from lotus.models import Author


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
