from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils.translation import gettext_lazy as _
from django.urls import translate_url, reverse

from smart_media.mixins import SmartFormatMixin
from smart_media.modelfields import SmartMediaField
from smart_media.signals import auto_purge_files_on_change, auto_purge_files_on_delete

from ..managers import CategoryManager

from .translated import Translated


class Category(SmartFormatMixin, Translated):
    """
    Category model.
    """
    original = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        help_text=_(
            "Mark this category as a translation of an original category."
        ),
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
        _("slug"),
        max_length=255,
    )
    """
    Required unique slug string.
    """

    lead = models.TextField(
        _("lead"),
        blank=True,
        help_text=_(
            "Lead paragraph, commonly used for SEO purposes in page meta tags."
        ),
    )
    """
    Optional text lead.
    """

    description = models.TextField(
        _("description"),
        blank=True,
    )
    """
    Optional description string.
    """

    cover = SmartMediaField(
        verbose_name=_("cover image"),
        upload_to="lotus/category/cover/%y/%m",
        max_length=255,
        blank=True,
        default="",
    )

    """
    Optional cover image file.
    """

    COMMON_ORDER_BY = ["title"]
    """
    List of field order commonly used in frontend view/api
    """

    objects = CategoryManager()

    class Meta:
        ordering = ["title"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "slug", "language"
                ],
                name="lotus_unique_cat_slug_lang"
            ),
            models.UniqueConstraint(
                fields=[
                    "original", "language"
                ],
                name="lotus_unique_cat_original_lang"
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return absolute URL to the category detail view.

        Returns:
            string: An URL.
        """
        return translate_url(
            reverse("lotus:category-detail", kwargs={
                "slug": self.slug,
            }),
            self.language
        )

    def get_cover_format(self):
        return self.media_format(self.cover)


# Connect some signals
post_delete.connect(
    auto_purge_files_on_delete(["cover"]),
    dispatch_uid="category_cover_on_delete",
    sender=Category,
    weak=False,
)
pre_save.connect(
    auto_purge_files_on_change(["cover"]),
    dispatch_uid="category_cover_on_change",
    sender=Category,
    weak=False,
)
