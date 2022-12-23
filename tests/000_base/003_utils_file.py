import uuid
from pathlib import Path

import pytest
from freezegun import freeze_time

from lotus.utils.file import get_unique_filename, uploadto_unique


@pytest.mark.parametrize("filename, expected", [
    ("foo.jpg", [".jpg"]),
    ("ping.tar.gz", [".tar", ".gz"]),
    ("bar", []),
])
def test_get_unique_filename(filename, expected):
    """
    Function should return a new filename with original name replaced but file
    extensions keeped and it should work also with filename without any extensions.
    """
    result = get_unique_filename(filename)

    assert result != filename
    assert Path(result).suffixes == expected


@freeze_time("2012-10-15 10:00:00")
@pytest.mark.parametrize("path, filename, expected", [
    ("ping/pong", "foo.jpg", "ping/pong/an_uuid.jpg"),
    ("ping/%Y/%m/%d", "foo.tar.gz", "ping/2012/10/15/an_uuid.tar.gz"),
    ("ping/%m/%d/pong", "foo", "ping/10/15/pong/an_uuid"),
])
def test_uploadto_unique(monkeypatch, path, filename, expected):
    """
    Function should return a callable that can be used to build a path with a date
    and an unique filename.

    However in this test there is no uniqueness assertion since we mockup uuid4 since
    we can not predict its returned value.
    """
    def mockuuid4():
        # Always return the same dummy value instead of unpredictable id.
        return "an_uuid"

    monkeypatch.setattr(uuid, "uuid4", mockuuid4)

    assert str(uploadto_unique(path, None, filename)) == expected
