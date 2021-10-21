"""
==============
Article models
==============

"""
import datetime

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate as translation_activate
from django.utils.translation import deactivate as translation_deactivate
from django.urls import reverse
from django.utils import timezone

from ..choices import get_status_choices, get_status_default
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
        choices=get_status_choices(),
        default=get_status_default(),
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

    seo_title = models.CharField(
        _("SEO title"),
        blank=True,
        max_length=150,
        default="",
        help_text=_(
            "This value Will be used as page meta title if not blank, else the "
            "article title is used."
        ),
    )
    """
    Optional SEO title string used as meta title if not blank, instead of default
    behavior to use article title.
    """

    lead = models.TextField(
        _("lead"),
        blank=True,
        help_text=_(
            "Lead paragraph, mostly used for SEO purposes in page metas."
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

    COMMON_ORDER_BY = ["-pinned", "-publish_date", "-publish_time", "title"]
    """
    List of field order commonly used in frontend view/api
    """

    objects = ArticleManager()

    class Meta:
        ordering = [
            "-publish_date",
            "-publish_time",
            "title",
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

        Returns:
            string: An URL.
        """
        # Force the article language to get the right url independently of the current
        # browser language. This is not thread safe, deactivate must be called once
        # rendering is finished.
        translation_activate(self.language)

        url = reverse("lotus:article-detail", kwargs={
            "year": self.publish_date.year,
            "month": self.publish_date.month,
            "day": self.publish_date.day,
            "slug": self.slug,
        })

        translation_deactivate()

        return url

    def get_authors(self):
        """
        Return article authors.

        Returns:
            queryset: List of article authors.
        """
        return self.authors.all().order_by("first_name", "last_name")

    def get_categories(self):
        """
        Return article categories, results are enforced on article language.

        Returns:
            queryset: List of article categories.
        """
        return self.categories.get_for_lang(self.language).order_by("title")

    def get_related(self):
        """
        Return article related articles, results are enforced on article language.

        Returns:
            queryset: List of related articles.
        """
        return self.related.get_for_lang(self.language).order_by(
            *self.COMMON_ORDER_BY
        )

    def publish_datetime(self):
        """
        Return a datetime from joined publish date and time.

        Returns:
            datetime.datetime: Publish datetime.
        """
        return datetime.datetime.combine(
            self.publish_date, self.publish_time
        ).replace(tzinfo=timezone.utc)

    def get_states(self, now=None):
        """
        Computate every publication states.

        State names depend from ``settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES`` and
        each state name can be disabled (never raised in states) if their name key have
        been removed from setting.

        Keywords Arguments:
            now (datetime.datetime): Commonly the current datetime now  (timezone aware)
                which have been used in queryset lookup to check for publication
                availability. It is used to determine if article publish start date is
                to come next or if article publish end date is over the current date.
                Empty by default, there will be no state about start/end dates.

        Returns:
            datetime.datetime: Publish datetime.
        """
        state_names = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
        states = []

        if "pinned" in state_names and self.pinned:
            states.append(state_names["pinned"])

        if "featured" in state_names and self.featured:
            states.append(state_names["featured"])

        if "private" in state_names and self.private:
            states.append(state_names["private"])

        if "status_draft" in state_names and self.status < 10:
            states.append(state_names["status_draft"])

        if "status_available" in state_names and self.status == 10:
            states.append(state_names["status_available"])

        # Available article can describe if it is below the publish start or over the
        # publish end
        if now and self.status == 10:
            if (
                "publish_start_below" in state_names and
                self.publish_datetime() > now
            ):
                states.append(state_names["publish_start_below"])

            if (
                "publish_end_passed" in state_names and
                self.publish_end and
                self.publish_end < now
            ):
                states.append(state_names["publish_end_passed"])

        return states

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
