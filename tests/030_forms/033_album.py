from lotus.factories import AlbumFactory
from lotus.forms import AlbumAdminForm
from lotus.models import Album
from lotus.utils.tests import build_post_data_from_object


def test_album_admin_change_form(db):
    """
    Ensure the admin change form is working well (this should media add form
    also) and ensure image upload is correct.
    """
    # Create new object without a media file
    obj = AlbumFactory.build()

    # Build initial POST data
    ignore = ["id"]
    data = build_post_data_from_object(Album, obj, ignore=ignore)
    file_data = {}

    f = AlbumAdminForm(data, file_data, instance=obj)

    # No validation errors
    assert f.is_valid() is True
    assert f.errors.as_data() == {}

    updated_obj = f.save()

    # Check everything has been saved
    assert updated_obj.title == obj.title

    assert Album.objects.count() == 1
