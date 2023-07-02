"""
Django settings for tests
"""
from sandbox.settings.base import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Media directory dedicated to tests to avoid polluting other environment
# media directory
MEDIA_ROOT = VAR_PATH / "media-tests"  # noqa: F405

# All resolved full URLs from API start with this prefix
# No ending slash. This is reserved to test only and has no purpose for other
# environments
LOTUS_API_TEST_BASEURL = "http://testserver"