from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from smart_media.admin import SmartModelAdmin

from ..forms import AlbumAdminForm, AlbumItemAdminForm
from ..models import Album, AlbumItem


class AlbumItemAdmin(admin.TabularInline):
    """
    Item admin to use as an inline form inside Album admin.
    """
    model = AlbumItem
    form = AlbumItemAdminForm
    extra = 0
    verbose_name = _("Album item")
    ordering = AlbumItem.COMMON_ORDER_BY
    formfield_overrides = SmartModelAdmin.formfield_overrides
    list_display = (
        "title",
        "order",
        "media",
    )


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    model = Album
    form = AlbumAdminForm
    verbose_name = _("Album")
    ordering = ["title"]
    list_display = (
        "title",
    )
    inlines = (AlbumItemAdmin,)

    class Media:
        css = settings.LOTUS_ADMIN_ALBUM_ASSETS.get("css", None)
        js = settings.LOTUS_ADMIN_ALBUM_ASSETS.get("js", None)
