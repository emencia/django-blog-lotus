import datetime
import json
from pathlib import Path

from taggit.models import Tag

from ..models import Album, Article, Author, Category


class ExtendedJsonEncoder(json.JSONEncoder):
    """
    Additional opiniated support for more basic object types.

    Usage sample: ::

        json.dumps(..., cls=ExtendedJsonEncoder)
    """
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        # Support for pathlib.Path to a string
        if isinstance(obj, Path):
            return str(obj)
        # Support for set to a list
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        if isinstance(obj, Album):
            return repr(obj)
        if isinstance(obj, Article):
            return repr(obj)
        if isinstance(obj, Author):
            return repr(obj)
        if isinstance(obj, Category):
            return repr(obj)
        if isinstance(obj, Tag):
            return repr(obj)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
