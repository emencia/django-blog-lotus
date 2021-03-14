"""
==========
Translated
==========

"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Translated(models.Model):
    """
    Abstract model for common content translation fields
    """
    language = models.CharField(
        _("language"),
        blank=False,
        max_length=8,
        default=settings.LANGUAGE_CODE,
    )
    """
    Required language code.
    """

    class Meta:
        abstract = True
