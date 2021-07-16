"""
Article admin interface
"""
from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..forms import ArticleAdminForm
from ..models import Article
from ..choices import STATUS_PUBLISHED

from .translated import LanguageListFilter


# Shortcut to get setting as a dict
LANGUAGE_NAMES = dict(settings.LANGUAGES)


class ArticleAdmin(admin.ModelAdmin):
    """
    TODO:
        A new 'list_filter' to filter on a category?
    """
    form = ArticleAdminForm
    list_display = (
        "title",
        "language_name",
        "is_published",
        "private",
        "publish_datetime",
        "last_update",
    )
    list_filter = (
        LanguageListFilter,
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    ordering = (
        "publish_date",
        "publish_time",
        "title",
    )
    search_fields = [
        "title",
    ]
    filter_horizontal = (
        "categories",
        "authors",
        "related",
    )
    fieldsets = (
        (
            None, {
                "fields": (
                    "title",
                    "slug",
                )
            }
        ),
        (
            _("Language"), {
                "fields": (
                    ("language", "original"),
                )
            }
        ),
        (
            _("Parameters"), {
                "fields": (
                    "status",
                    ("featured", "pinned", "private"),
                )
            }
        ),
        (
            _("Dates"), {
                "fields": (
                    ("publish_date", "publish_time"),
                    "publish_end",
                )
            }
        ),
        (
            _("Content"), {
                "fields": (
                    "cover",
                    "introduction",
                    "image",
                    "content",
                )
            }
        ),
        (
            _("SEO"), {
                "fields": (
                    "seo_title",
                    "lead",
                )
            }
        ),
        (
            _("Relations"), {
                "fields": (
                    "categories",
                    "authors",
                    "related",
                )
            }
        ),
    )

    def language_name(self, obj):
        return LANGUAGE_NAMES[obj.language]
    language_name.short_description = _("language")

    def publish_datetime(self, obj):
        return obj.publish_datetime()
    publish_datetime.short_description = _("publish date")

    def is_published(self, obj):
        now = timezone.now()

        return (
            obj.status == STATUS_PUBLISHED and
            obj.publish_datetime() <= now and
            (obj.publish_end is None or obj.publish_end > now)
        )
    is_published.short_description = _("published ?")
    is_published.boolean = True

    def view_on_site(self, obj):
        """
        Add request argument to bypass publication criteria on view queryset.
        """
        return obj.get_absolute_url() + "?admin=1"


# Registering interface to model
admin.site.register(Article, ArticleAdmin)
