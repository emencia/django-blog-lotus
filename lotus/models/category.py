from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import translate_url, reverse

from treebeard.mp_tree import MP_Node

from smart_media.mixins import SmartFormatMixin
from smart_media.modelfields import SmartMediaField
from smart_media.signals import auto_purge_files_on_change, auto_purge_files_on_delete

from ..managers import CategoryManager
from ..exceptions import LanguageMismatchError
from .translated import Translated


class Category(SmartFormatMixin, MP_Node, Translated):
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

    modified = models.DateTimeField(
        _("modification date"),
        default=timezone.now,
        editable=False,
    )
    """
    Automatic modification date.
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

    node_order_by = ["title"]
    """
    Treebeard attribute used for ordering with position name
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
            reverse("lotus:category-detail", kwargs={"slug": self.slug}),
            self.language
        )

    def get_absolute_api_url(self):
        """
        Return absolute URL to the author detail viewset from API.

        Returns:
            string: An URL.
        """
        return reverse("lotus-api:category-detail", kwargs={"pk": self.id})

    def get_edit_url(self):
        """
        Return absolute URL to edit category from admin.

        Returns:
            string: An URL.
        """
        return reverse("admin:lotus_category_change", args=(self.id,))

    def get_subcategories(self):
        """
        Return category children, results are enforced on category language.

        Returns:
            queryset: List of children categories.
        """
        if not self.numchild:
            return []

        return self.get_children().filter(language=self.language).order_by("title")

    def get_cover_format(self):
        return self.media_format(self.cover)

    def move_into(self, parent):
        """
        Move object as a child of given parent.

        This is a shortcut around MP_Node.move() method but with positionning forced
        on 'sorted child' technic because it is the only one that fit to Lotus needs.

        You should never try to manually set a Category as a child of a parent
        Category because it will probably not correctly manage the node path rewriting.

        Raises:
            LanguageMismatchError: If both object language and parent language
                are differents.

        Arguments:
            parent (Category): A category object to define as the parent.
        """
        # Enforce language validation before performing tree insertion
        if parent.language != self.language:
            msg = (
                "Object with language '{current_lang}' can not be moved as a child of "
                "another object with language '{parent_lang}'"
            )
            raise LanguageMismatchError(msg.format(
                parent_lang=parent.language,
                current_lang=self.language,
            ))

        self.move(parent, pos="sorted-child")

    def save(self, *args, **kwargs):
        # Auto update 'modified' value on each save
        self.modified = timezone.now()

        super().save(*args, **kwargs)


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
