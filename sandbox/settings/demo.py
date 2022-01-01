"""
Django settings for demonstration

Intended to be used with ``make run``.
"""
from sandbox.settings.base import *

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": join(VAR_PATH, "db", "db.sqlite3"),  # noqa
    }
}

# Upgrade limit to fit to layout
LOTUS_CATEGORY_PAGINATION = 10
LOTUS_ARTICLE_PAGINATION = 16
LOTUS_AUTHOR_PAGINATION = 12

# Import local settings if any
try:
    from .local import *
except ImportError:
    pass
