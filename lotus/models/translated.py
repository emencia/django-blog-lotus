from django.db import models
from django.utils.translation import gettext_lazy as _

from ..choices import get_language_choices, get_language_default


class Translated(models.Model):
    """
    Abstract model for common content translation fields.
    """
    language = models.CharField(
        _("language"),
        blank=False,
        db_index=True,
        max_length=8,
        choices=get_language_choices(),
        default=get_language_default(),
    )
    """
    Required language code.
    """

    class Meta:
        abstract = True
