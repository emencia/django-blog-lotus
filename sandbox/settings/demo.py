"""
Django settings for demonstration

Intended to be used with ``make run``.
"""
from sandbox.settings.base import *  # noqa: F403

DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": VAR_PATH / "db" / "db.sqlite3",  # noqa: F405
    }
}

# Upgrade limit to fit to layout
LOTUS_CATEGORY_PAGINATION = 10
LOTUS_ARTICLE_PAGINATION = 16
LOTUS_AUTHOR_PAGINATION = 12

# Enable 'drf_redesign' only if it is installed and DRF also
if API_AVAILABLE:  # noqa: F405
    try:
        import drf_redesign  # noqa: F401
    except ModuleNotFoundError:
        pass
    else:
        # App need to be enabled before DRF
        INSTALLED_APPS.insert(  # noqa: F405
            INSTALLED_APPS.index("rest_framework") - 1, "drf_redesign"  # noqa: F405
        )

# Import local settings if any
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
