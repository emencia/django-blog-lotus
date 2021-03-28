"""
=======
Article
=======

"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone

from ..choices import STATUS_DRAFT, STATUS_PUBLISHED, STATUS_CHOICES
from ..managers import ArticleManager

from .translated import Translated


class Article(Translated):
    """
    Article model.

    TODO:
        A lot of needed/useful content fields are missing.
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

    publish_start = models.DateTimeField(
        "publication start",
        db_index=True,
        default=timezone.now,
    )
    """
    Required publication start date.
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
    Last edition date
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

    content = models.TextField(
        _("content"),
        blank=True,
        default="",
    )
    """
    Optionnal text content.
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
            # NOTE: Not sure it's enough, since we plan to have urls without lang
            # when disabled multilang and so there could be same slug+date
            # resolving which lead to a multiple objects error for detail.
            models.UniqueConstraint(
                fields=[
                    "publish_start", "slug", "language"
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
