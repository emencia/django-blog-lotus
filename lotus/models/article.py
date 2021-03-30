"""
==============
Article models
==============

"""
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone

from ..choices import STATUS_DRAFT, STATUS_CHOICES
from ..managers import ArticleManager
from ..signals import (
    auto_purge_media_files_on_delete, auto_purge_media_files_on_change,
)

from .translated import Translated


class Article(Translated):
    """
    Article model.
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

    status = models.SmallIntegerField(
        _("status"),
        db_index=True,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    """
    Required article status.
    """

    publish_date = models.DateField(
        "publication date",
        db_index=True,
        default=timezone.now,
    )
    """
    Required publication date.
    """

    publish_time = models.TimeField(
        "publication time",
        default=timezone.now,
    )
    """
    Required publication date.
    """

    publish_end = models.DateTimeField(
        "publication end",
        db_index=True,
        default=None,
        null=True,
        blank=True,
    )
    """
    Optional publication end date.
    """

    last_update = models.DateTimeField(
        _('last update'),
        default=timezone.now,
    )
    """
    Last edition date.
    """

    title = models.CharField(
        _("title"),
        blank=False,
        max_length=150,
        default="",
    )
    """
    Required title string.
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
    )
    """
    Optionnal text lead.
    """

    introduction = models.TextField(
        _('introduction'),
        blank=True,
    )
    """
    Optionnal text introduction.
    """

    content = models.TextField(
        _("content"),
        blank=True,
        default="",
    )
    """
    Optionnal text content.
    """

    cover = models.ImageField(
        verbose_name=_("cover image"),
        upload_to="lotus/article/cover/%y/%m",
        max_length=255,
        blank=True,
        default="",
    )
    """
    Optionnal cover image.
    """

    image = models.ImageField(
        verbose_name=_("main image"),
        upload_to="lotus/article/image/%y/%m",
        max_length=255,
        blank=True,
        default="",
    )
    """
    Optionnal cover image.
    """

    categories = models.ManyToManyField(
        "lotus.Category",
        verbose_name=_("categories"),
        related_name="articles",
        blank=True,
    )
    """
    Related Categories.
    """

    authors = models.ManyToManyField(
        'lotus.Author',
        verbose_name=_('authors'),
        related_name='articles',
        blank=True,
    )
    """
    Related Authors.
    """

    objects = ArticleManager()

    class Meta:
        ordering = ["title"]
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        constraints = [
            # Enforce unique couple date + slug + lang
            models.UniqueConstraint(
                fields=[
                    "publish_date", "slug", "language"
                ],
                name="lotus_unique_art_pub_slug_lang"
            ),
            # Enforce no multiple translations for the same language
            models.UniqueConstraint(
                fields=[
                    "original", "language"
                ],
                name="lotus_unique_art_original_lang"
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return absolute URL to the article detail view.

        Returns:
            string: An URL.
        """
        return reverse("lotus:article-detail", args=[
            str(self.id),
        ])

    def save(self, *args, **kwargs):
        # Auto update last_update on each save
        self.last_update = timezone.now()

        super().save(*args, **kwargs)


# Connect some signals
post_delete.connect(
    auto_purge_media_files_on_delete,
    dispatch_uid="article_medias_on_delete",
    sender=Article,
)
pre_save.connect(
    auto_purge_media_files_on_change,
    dispatch_uid="article_medias_on_change",
    sender=Article,
)
