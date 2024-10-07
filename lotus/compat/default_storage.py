"""
The old way to get a storage object has been deprecated since ``Django 4.2`` and
removed since ``Django 5.1``.

This modules should safely get and initialize the default storage class for
``Django>=3.8`` adn exposes it as a variable ``DEFAULT_STORAGE``.
"""
try:
    # Attempt to check for Django>=5.0 behavior
    from django.core.files.storage import storages  # noqa: F401,F403
except ImportError:
    # Fallback to Django<=4.2 behavior
    from django.core.files.storage import get_storage_class
    DEFAULT_STORAGE = get_storage_class()()  # noqa: F401,F403
else:
    # Result for Django>=5.0
    from django.conf import settings
    from django.utils.module_loading import import_string
    DEFAULT_STORAGE = import_string(
        settings.STORAGES["default"]["BACKEND"]
    )()  # noqa: F401,F403
