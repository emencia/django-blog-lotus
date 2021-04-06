import os

from django.core.files.uploadedfile import SimpleUploadedFile

from lotus.factories import ArticleFactory
from lotus.forms import ArticleAdminForm
from lotus.models import Article
from lotus.utils.tests import (
    DUMMY_GIF_BYTES,
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
)


def test_article_admin_add(db, admin_client):
    """
    Article model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(Article)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_list(db, admin_client):
    """
    Article model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(Article)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_detail(db, admin_client):
    """
    Article model admin detail view should not raise error on GET request.
    """
    obj = ArticleFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_change_form(db, admin_client):
    """
    Ensure the admin change form is working well (this should cover add form
    also) and ensure image upload is correct.
    """
    # Create new object without a cover file
    obj = ArticleFactory(
        cover=None,
        image=None,
        fill_categories=True,
        fill_authors=True,
    )

    # Fields we don't want to post anything
    ignored_fields = ["id", "relations", "article"]

    # Build POST data from object field values
    data = {}
    fields = [
        f.name for f in Article._meta.get_fields()
        if f.name not in ignored_fields
    ]
    for name in fields:
        value = getattr(obj, name)
        # M2M are special ones since form expect only a list of IDs
        if name in ("categories", "authors", "related"):
            data[name] = value.values_list("id", flat=True)
        else:
            data[name] = value

    file_data = {
        "cover": SimpleUploadedFile(
            "small.gif",
            DUMMY_GIF_BYTES,
            content_type="image/gif"
        ),
        "image": SimpleUploadedFile(
            "large.gif",
            DUMMY_GIF_BYTES,
            content_type="image/gif"
        ),
    }

    f = ArticleAdminForm(data, file_data, instance=obj)

    # No validation errors
    assert f.is_valid() is True
    assert f.errors.as_data() == {}

    updated_obj = f.save()

    # Check everything has been saved
    assert updated_obj.title == obj.title
    assert os.path.exists(obj.cover.path) is True
    assert os.path.exists(obj.image.path) is True
