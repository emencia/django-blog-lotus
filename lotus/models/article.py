"""
=======
Article
=======

"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

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
        _('slug'),
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
        verbose_name="catégories",
        related_name="articles",
        blank=True,
    )
    """
    Related Categories.
    """

    class Meta:
        ordering = ['title']
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "title", "language"
                ],
                name='unique_article_title_for_lang'
            ),
            models.UniqueConstraint(
                fields=[
                    "slug", "language"
                ],
                name='unique_article_slug_for_lang'
            ),
            models.UniqueConstraint(
                fields=[
                    "original", "language"
                ],
                name='unique_article_original_for_lang'
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
