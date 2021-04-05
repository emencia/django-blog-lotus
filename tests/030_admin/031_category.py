import os

from django.core.files.uploadedfile import SimpleUploadedFile

from lotus.factories import CategoryFactory
from lotus.forms import CategoryAdminForm
from lotus.models import Category
from lotus.utils.tests import (
    DUMMY_GIF_BYTES,
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
)


def test_category_admin_add(db, admin_client):
    """
    Category model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(Category)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_list(db, admin_client):
    """
    Category model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(Category)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_detail(db, admin_client):
    """
    Category model admin detail view should not raise error on GET request.
    """
    obj = CategoryFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_change_form(db, admin_client):
    """
    Ensure the admin change form is working well (this should cover add form
    also) and ensure image upload is correct.
    """
    # Create new object without a cover file
    obj = CategoryFactory(cover=None)

    # Fields we don't want to post anything or relation attributes which are
    # not model fields
    ignored_fields = ["id", "category", "articles"]

    # Build POST data from object field values
    data = {}
    fields = [
        f.name for f in Category._meta.get_fields()
        if f.name not in ignored_fields
    ]
    for name in fields:
        value = getattr(obj, name)
        data[name] = value

    file_data = {
        "cover": SimpleUploadedFile(
            "small.gif",
            DUMMY_GIF_BYTES,
            content_type="image/gif"
        ),
    }

    f = CategoryAdminForm(data, file_data, instance=obj)

    # No validation errors
    assert f.is_valid() is True
    assert f.errors.as_data() == {}

    updated_obj = f.save()

    # Check everything has been saved
    assert updated_obj.title == obj.title
    assert os.path.exists(obj.cover.path) is True
