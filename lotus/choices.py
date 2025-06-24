from django.conf import settings
from django.utils.translation import gettext_lazy as _


STATUS_DRAFT = 0
"""
Draft status numeric value
"""

STATUS_PUBLISHED = 10
"""
Published status numeric value
"""

STATUS_CHOICES = (
    (STATUS_DRAFT, _("draft")),
    (STATUS_PUBLISHED, _("available"))
)
"""
Status choice list
"""


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


def get_article_template_choices():
    """
    Callable to get Article template choice list.
    """
    return settings.LOTUS_ARTICLE_DETAIL_TEMPLATES


def get_article_template_default():
    """
    Callable to get default Article template.
    """
    return settings.LOTUS_ARTICLE_DETAIL_TEMPLATES[0][0]


def get_category_template_choices():
    """
    Callable to get Category template choice list.
    """
    return settings.LOTUS_CATEGORY_DETAIL_TEMPLATES


def get_category_template_default():
    """
    Callable to get default Category template.
    """
    return settings.LOTUS_CATEGORY_DETAIL_TEMPLATES[0][0]
