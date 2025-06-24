import datetime

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import translate_url, reverse

from taggit.managers import TaggableManager

from smart_media.mixins import SmartFormatMixin
from smart_media.modelfields import SmartMediaField
from smart_media.signals import auto_purge_files_on_change, auto_purge_files_on_delete

from ..choices import (
    STATUS_PUBLISHED, get_status_choices, get_status_default,
    get_article_template_choices, get_article_template_default,
)
from ..managers import ArticleManager

from .translated import Translated


class Article(SmartFormatMixin, Translated):
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
            "Mark this article as a translation of an original article."
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
    Required publication time.
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
            "Used to build the article URL."
        ),
    )
    """
    Required unique slug string.
    """

    template = models.CharField(
        _("template"),
        blank=False,
        max_length=150,
        choices=get_article_template_choices(),
        default=get_article_template_default(),
    )
    """
    Optional custom template path string.
    """

    seo_title = models.CharField(
        _("SEO title"),
        blank=True,
        max_length=150,
        default="",
        help_text=_(
            "This value will be used as page meta title if not blank, else the "
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
            "Lead paragraph, commonly used for SEO purposes in page meta tags."
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

    cover = SmartMediaField(
        verbose_name=_("cover image"),
        upload_to="lotus/article/cover/%y/%m",
        max_length=255,
        blank=True,
        default="",
        help_text=_("Article cover image."),
    )
    """
    Optional cover image.
    """

    cover_alt_text = models.CharField(
        _("cover alternative text"),
        blank=True,
        max_length=125,
        default="",
    )
    """
    Optional alternative text for cover image.
    """

    image = SmartMediaField(
        verbose_name=_("main image"),
        upload_to="lotus/article/image/%y/%m",
        max_length=255,
        blank=True,
        default="",
        help_text=_("Article large image."),
    )
    """
    Optional main image.
    """

    image_alt_text = models.CharField(
        _("main alternative text"),
        blank=True,
        max_length=125,
        default="",
    )
    """
    Optional alternative text for main image.
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

    tags = TaggableManager(blank=True)
    """
    Optional tags
    """

    album = models.ForeignKey(
        "lotus.Album",
        related_name="articles",
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    """
    Optional album relation.
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

    def build_absolute_url(self, urlname):
        """
        Build object absolute URL with language prefix for url name.

        Language is forced on article language.

        Arguments:
            urlname (string): The URL name to reverse with kwargs to get absolute URL.

        Returns:
            string: Object absolute URL.
        """
        return translate_url(
            reverse(urlname, kwargs={
                "year": self.publish_date.year,
                "month": self.publish_date.month,
                "day": self.publish_date.day,
                "slug": self.slug,
            }),
            self.language
        )

    def get_absolute_url(self):
        """
        Return absolute URL to the article detail view.

        Returns:
            string: An URL.
        """
        return self.build_absolute_url("lotus:article-detail")

    def get_absolute_api_url(self):
        """
        Return absolute URL to the article detail viewset from API.

        Returns:
            string: An URL.
        """
        return reverse("lotus-api:article-detail", kwargs={"pk": self.id})

    def get_absolute_preview_url(self):
        """
        Return absolute URL to the article detail view in forced preview mode.

        Returns:
            string: An URL.
        """
        return self.build_absolute_url("lotus:preview-article-detail")

    def get_edit_url(self):
        """
        Return absolute URL to edit article from admin.

        Returns:
            string: An URL.
        """
        return reverse("admin:lotus_article_change", args=(self.id,))

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

        .. Todo::

            This should use Category.COMMON_ORDER_BY instead of hardcoded field (even
            it is right)

        Returns:
            queryset: List of article categories.
        """
        return self.categories.get_for_lang(self.language).order_by("title")

    def get_album_items(self):
        """
        Return album items.

        Depends on ``use_original_album`` value.

        Returns:
            queryset: List of album items.
        """
        return []

    def get_related(self, filter_func=None):
        """
        Return article related articles.

        .. Warning::
            On  default without ``filter_func`` defined this won't apply any
            publication criteria, only the language filtering.

            You would need to give it a proper filtering function to ensure about
            results.

        TODO: Concretely for now, the 'filter_func' is not used in HTML frontend but it
        should, either from a variable context or a template tag.

        Keyword Arguments:
            filter_func (function): A function used to create a queryset for related
                articles filtered. It has been done to be given
                ``ArticleFilterMixin.apply_article_lookups`` so any other given
                function should at least expect the same arguments.

        Returns:
            queryset: List of related articles.
        """
        if filter_func:
            q = filter_func(self.related, self.language)
        else:
            q = self.related.get_for_lang(self.language)

        return q.order_by(*self.COMMON_ORDER_BY)

    def get_tags(self):
        """
        Return article tags.

        Returns:
            queryset: List of related 'taggit.models.Tag' objects.
        """
        return self.tags.all()

    def publish_datetime(self):
        """
        Return a datetime from joined publish date and time.

        Returns:
            datetime.datetime: Publish datetime with UTC timezone.
        """
        return datetime.datetime.combine(
            self.publish_date, self.publish_time
        ).replace(tzinfo=datetime.timezone.utc)

    def get_states(self, now=None):
        """
        Computate every publication states.

        State names depend from ``settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES`` and
        each state name can be disabled (never raised in states) if its key name have
        been removed from setting.

        Keywords Arguments:
            now (datetime.datetime): Commonly the current datetime 'now' (timezone
                aware) which have been used in queryset lookup to check for publication
                availability. It is used to determine if article publish "start date"
                is to come next or if article publish "end date" is over the current
                date. Empty by default, there will be no state about start/end dates.

        Returns:
            list: A list of all article state names.
        """
        state_names = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
        states = []

        if "pinned" in state_names and self.pinned:
            states.append(state_names["pinned"])

        if "featured" in state_names and self.featured:
            states.append(state_names["featured"])

        if "private" in state_names and self.private:
            states.append(state_names["private"])

        if "status_draft" in state_names and self.status < STATUS_PUBLISHED:
            states.append(state_names["status_draft"])

        if "status_available" in state_names and self.status == STATUS_PUBLISHED:
            states.append(state_names["status_available"])

        # Available article describes if it is below the publish start or over the
        # publish end, but only if "now" have been given
        if now and self.status == STATUS_PUBLISHED:
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

    def is_published(self, now=None):
        """
        Check for all publication criterias for a datetime.

        Keywords Arguments:
            now (datetime.datetime): Datetime to match against for publication states.
                Default to ``None`` so it will use current datetime.

        Returns:
            boolean: True if object is published else False.
        """
        state_names = settings.LOTUS_ARTICLE_PUBLICATION_STATE_NAMES
        states = self.get_states(now or timezone.now())

        return (
            state_names["status_available"] in states and
            state_names["status_draft"] not in states and
            state_names["publish_start_below"] not in states and
            state_names["publish_end_passed"] not in states
        )

    def get_cover_format(self):
        return self.media_format(self.cover)

    def get_image_format(self):
        return self.media_format(self.image)

    def save(self, *args, **kwargs):
        # Auto update 'last_update' value on each save
        self.last_update = timezone.now()

        super().save(*args, **kwargs)


# Connect signals for automatic media purge
post_delete.connect(
    auto_purge_files_on_delete(["cover", "image"]),
    dispatch_uid="article_medias_on_delete",
    sender=Article,
    weak=False,
)
pre_save.connect(
    auto_purge_files_on_change(["cover", "image"]),
    dispatch_uid="article_medias_on_change",
    sender=Article,
    weak=False,
)
