from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from smart_media.mixins import SmartFormatMixin
from smart_media.modelfields import SmartMediaField
from smart_media.signals import auto_purge_files_on_change, auto_purge_files_on_delete


class Album(models.Model):
    """
    Album container for items.
    """
    title = models.CharField(
        _("Title"),
        blank=False,
        max_length=150,
        default="",
    )
    """
    A required title string.
    """

    modified = models.DateTimeField(
        _("modification date"),
        default=timezone.now,
        editable=False,
    )
    """
    Automatic modification date.
    """

    class Meta:
        verbose_name = _("Album")
        verbose_name_plural = _("Albums")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto update 'modified' value on each save
        self.modified = timezone.now()

        super().save(*args, **kwargs)


class AlbumItem(SmartFormatMixin, models.Model):
    """
    Album item model.
    """
    album = models.ForeignKey(
        "lotus.Album",
        related_name="albumitems",
        on_delete=models.CASCADE
    )

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
        blank=True,
        max_length=150,
        default="",
    )
    """
    Required title string.
    """

    order = models.IntegerField(
        _("Order"),
        blank=False,
        default=0
    )
    """
    Optional number for order position in item list.
    """

    media = SmartMediaField(
        verbose_name=_("File"),
        upload_to="lotus/album/media/%y/%m",
        max_length=255,
        default="",
    )
    """
    Required media file.
    """

    COMMON_ORDER_BY = ["order", "title"]
    """
    List of field order commonly used in frontend view/api
    """

    class Meta:
        ordering = [
            "order",
            "title",
        ]
        verbose_name = _("Article album")
        verbose_name_plural = _("Articles albums")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id and not self.title:
            self.title = self.media.name

        # Auto update 'modified' value on each save
        self.modified = timezone.now()

        super().save(*args, **kwargs)


# Connect signals for automatic media purge
post_delete.connect(
    auto_purge_files_on_delete(["media"]),
    dispatch_uid="albumitem_medias_on_delete",
    sender=AlbumItem,
    weak=False,
)
pre_save.connect(
    auto_purge_files_on_change(["media"]),
    dispatch_uid="albumitem_medias_on_change",
    sender=AlbumItem,
    weak=False,
)
