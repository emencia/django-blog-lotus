"""
Django settings with Jazzmin app enabled

Intended to be used with ``make run-jazzmin``.
"""
from sandbox.settings.demo import *  # noqa: F403

INSTALLED_APPS[0:0] = [
    "jazzmin",
]
