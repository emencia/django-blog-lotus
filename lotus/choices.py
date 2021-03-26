"""
Application field choices
"""
from django.utils.translation import gettext_lazy as _

STATUS_DRAFT = 0
STATUS_PUBLISHED = 10

STATUS_CHOICES = (
    (STATUS_DRAFT, _('draft')),
    (STATUS_PUBLISHED, _('available'))
)

