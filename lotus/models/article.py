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
        verbose_name=_("original article"),
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        help_text=_(
            "Mark this article as a translation of original article."
        ),
    )
    """
    Optional original category when object is a translation.
    """

    status = models.SmallIntegerField(
        _("status"),
        db_index=True,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        help_text=_(
            "Publication status."
        ),
    )
    """
    Required article status.
    """

    featured = models.BooleanField(
        verbose_name=_("featured"),
        default=False,
        blank=True,
        help_text=_(
            "Mark this article as featured."
        ),
    )
    """
    Optional article featured mark.
    """

    pinned = models.BooleanField(
        verbose_name=_("pinned"),
        default=False,
        blank=True,
        help_text=_(
            "A pinned article is enforced at top of order results."
        ),
    )
    """
    Optional article pinned mark.
    """

    private = models.BooleanField(
        verbose_name=_("private"),
        default=False,
        blank=True,
        help_text=_(
            "Private article is only available for authenticated users."
        ),
    )
    """
    Optional privacy.
    """

    publish_date = models.DateField(
        _("publication date"),
        db_index=True,
        default=timezone.now,
        help_text=_(
            "Start date of publication."
        ),
    )
    """
    Required publication date.
    """

    publish_time = models.TimeField(
        _("publication time"),
        default=timezone.now,
        help_text=_(
            "Start time of publication."
        ),
    )
    """
    Required publication date.
    """

    publish_end = models.DateTimeField(
        _("publication end"),
        db_index=True,
        default=None,
        null=True,
        blank=True,
        help_text=_(
            "End date of publication."
        ),
    )
    """
    Optional publication end date.
    """

    last_update = models.DateTimeField(
        _("last update"),
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
        help_text=_(
            "Used to build the entry's URL."
        ),
    )
    """
    Required unique slug string.
    """

    lead = models.TextField(
        _("lead"),
        blank=True,
        help_text=_(
            "Lead paragraph, mostly used for SEO purposes."
        ),
    )
    """
    Optional text lead.
    """

    introduction = models.TextField(
        _("introduction"),
        blank=True,
    )
    """
    Optional text introduction.
    """

    content = models.TextField(
        _("content"),
        blank=True,
        default="",
    )
    """
    Optional text content.
    """

    cover = models.ImageField(
        verbose_name=_("cover image"),
        upload_to="lotus/article/cover/%y/%m",
        max_length=255,
        blank=True,
        default="",
        help_text=_(
            "Article cover image."
        ),
    )
    """
    Optional cover image.
    """

    image = models.ImageField(
        verbose_name=_("main image"),
        upload_to="lotus/article/image/%y/%m",
        max_length=255,
        blank=True,
        default="",
        help_text=_(
            "Article large image."
        ),
    )
    """
    Optional cover image.
    """

    categories = models.ManyToManyField(
        "lotus.Category",
        verbose_name=_("categories"),
        related_name="articles",
        blank=True,
    )
    """
    Optional related Categories.
    """

    authors = models.ManyToManyField(
        "lotus.Author",
        verbose_name=_("authors"),
        related_name="articles",
        blank=True,
    )
    """
    Optional related Authors.
    """

    related = models.ManyToManyField(
        "self",
        verbose_name=_("related articles"),
        related_name="relations",
        symmetrical=False,
        blank=True,
    )
    """
    Optional related article.
    """

    objects = ArticleManager()

    class Meta:
        ordering = ["title"]
        ordering = [
            "-publish_date",
            "-publish_time",
            "-title",
        ]
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

        TODO:
            Make the real url with slug+date+time and conditional language.

        Returns:
            string: An URL.
        """
        return reverse("lotus:article-detail", args=[
            str(self.id),
        ])

    def save(self, *args, **kwargs):
        # Auto update ``last_update`` value on each save
        self.last_update = timezone.now()

        super().save(*args, **kwargs)


# Connect signals for automatic media purge
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
