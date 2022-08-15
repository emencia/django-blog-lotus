"""
Django settings for external demonstration

Intended to be used with ``make run-demo``.
"""
from sandbox.settings.base import *  # noqa: F403

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": join(VAR_PATH, "db", "db.sqlite3"),  # noqa: F405
    }
}

# Upgrade limit to fit to layout
LOTUS_CATEGORY_PAGINATION = 10
LOTUS_ARTICLE_PAGINATION = 16
LOTUS_AUTHOR_PAGINATION = 12

SITE_ID = 2
