import pytest

from django.contrib.auth import get_user_model
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


@pytest.mark.django_db
def test_author_is_proxy_of_user_model():
    """
    Author should be a proxy for AUTH_USER_MODEL,
    regardless of whether it is the default User or a custom model.
    """
    UserModel = get_user_model()

    # Ensure that Author inherits directly from AUTH_USER_MODEL
    assert issubclass(Author, UserModel)
    assert Author._meta.proxy is True
    assert Author._meta.concrete_model is UserModel


@pytest.mark.django_db
def test_author_instance_behaves_like_user():
    """
    Author instances should behave like the user model instances
    (e.g., authentication and field access).
    """
    UserModel = get_user_model()

    # Create a user instance
    user = UserModel.objects.create_user(
        username="john", password="secret123", email="john@example.com"
    )

    # Retrieve the proxy Author instance for that user
    author = Author.objects.get(pk=user.pk)

    assert isinstance(author, Author)
    assert isinstance(author, UserModel)

    # Inherited fields and methods should work correctly
    assert author.username == "john"
    assert author.check_password("secret123")
    assert author.email == "john@example.com"
