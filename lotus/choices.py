"""
Application choices
"""
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# Constant values
STATUS_DRAFT = 0
STATUS_PUBLISHED = 10


# Choice list
STATUS_CHOICES = (
    (STATUS_DRAFT, _("draft")),
    (STATUS_PUBLISHED, _("available"))
)


def get_status_choices():
    """
    Callable to get choice list.
    """
    return STATUS_CHOICES


def get_status_default():
    """
    Callable to get default choice value.
    """
    return STATUS_DRAFT


def get_language_choices():
    """
    Callable to get available language choices.
    """
    return settings.LANGUAGES


def get_language_default():
    """
    Callable to get default language value.
    """
    return settings.LANGUAGE_CODE
