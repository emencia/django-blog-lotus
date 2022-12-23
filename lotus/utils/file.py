"""
==============
File utilities
==============

"""
import datetime

import uuid

from pathlib import Path


def get_unique_filename(filename):
    """
    Generate a new unique filename keeping file extension unchanged.

    Uniqueness is guaranteed by UUID.

    Arguments:
        filename (string): Original filename.

    Returns:
        pathlib.Path: Path for new filename.
    """
    return Path(
        str(uuid.uuid4())
    ).with_suffix(
        "".join(Path(filename).suffixes)
    )


def uploadto_unique(dirname, instance, filename):
    """
    Return a filepath with date patterns formatted and unique filename.

    So an usage like this: ::

        def file_uploadto(instance, filename):
            return uploadto_unique("ping/%Y/%m/%d", instance, filename))

        file = models.FileField("A file", upload_to=file_uploadto)

    Would save a file ``foo.jpg`` to a filepath like: ::

        ping/2012/10/15/16fd2706-8baf-433b-82eb-8c7fada847da.jpg

    Arguments:
        dirname (string): Directory path for storage, can include date patterns.
        instance (object): Model object instance.
        filename (string): Original filename.

    Returns:
        pathlib.Path: A Path object for the filepath to save.
    """
    dirname = Path(
        datetime.datetime.now().strftime(str(dirname))
    )

    return dirname / get_unique_filename(filename)
