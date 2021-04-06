"""
Application field choices
"""
from django.conf import settings
from django.utils.translation import gettext_lazy as _

STATUS_DRAFT = 0
STATUS_PUBLISHED = 10

STATUS_CHOICES = (
    (STATUS_DRAFT, _('draft')),
    (STATUS_PUBLISHED, _('available'))
)


def get_status_choices():
    return STATUS_CHOICES

def get_status_default():
    return STATUS_DRAFT

def get_language_choices():
    return settings.LANGUAGES

def get_language_default():
    return settings.LANGUAGE_CODE
