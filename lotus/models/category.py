"""
========
Category
========

"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from ..managers import CategoryManager

from .translated import Translated


class Category(Translated):
    """
    Category model.
    """
    original = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )
    """
    Optional original category when object is a translation.
    """

    title = models.CharField(
        _("title"),
        blank=False,
        max_length=255,
        default="",
    )
    """
    Required unique title string.
    """

    slug = models.SlugField(
        _('slug'),
        max_length=255,
    )
    """
    Required unique slug string.
    """

    description = models.TextField(
        _('description'),
        blank=True,
    )
    """
    Optional description string.
    """

    cover = models.ImageField(
        verbose_name="image de couverture",
        upload_to="lotus/cover/%y/%m",
        max_length=255,
        blank=True,
        default="",
    )
    """
    Optional cover image file.
    """

    objects = CategoryManager()

    class Meta:
        ordering = ['title']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "slug", "language"
                ],
                name='lotus_unique_cat_slug_lang'
            ),
            models.UniqueConstraint(
                fields=[
                    "original", "language"
                ],
                name='lotus_unique_cat_original_lang'
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return absolute URL to the blog detail view.

        Returns:
            string: An URL.
        """
        return reverse("lotus:category-detail", args=[
            str(self.id),
        ])
