"""
Article admin interface
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..forms import ArticleAdminForm
from ..models import Article
from ..choices import STATUS_PUBLISHED
from ..views.admin import ArticleAdminTranslateView

from .translated import LanguageListFilter


# Shortcut to get setting as a dict
LANGUAGE_NAMES = dict(settings.LANGUAGES)


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = (
        "title",
        "language_name",
        "is_published",
        "is_original",
        "pinned",
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
    ordering = Article.COMMON_ORDER_BY
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
        """
        Return humanized name for object language code.
        """
        return LANGUAGE_NAMES[obj.language]
    language_name.short_description = _("language")
    language_name.admin_order_field = "language"

    def publish_datetime(self, obj):
        """
        Return the merged publish date and time.
        """
        return obj.publish_datetime()
    publish_datetime.short_description = _("publish date")
    publish_datetime.admin_order_field = "-publish_date"

    def is_published(self, obj):
        """
        Check for all publication criterias.
        """
        now = timezone.now()

        return (
            obj.status == STATUS_PUBLISHED and
            obj.publish_datetime() <= now and
            (obj.publish_end is None or obj.publish_end > now)
        )
    is_published.short_description = _("published")
    is_published.boolean = True

    def is_original(self, obj):
        """
        Check article is an original or a translation.
        """
        return obj.original is None
    is_original.short_description = _("original")
    is_original.boolean = True

    def view_on_site(self, obj):
        """
        Add request argument to enable admin mode (to bypass publication criteria on
        frontend querysets).
        """
        return obj.get_absolute_url() + "?admin=1"

    def get_urls(self):
        """
        Set some additional custom admin views
        """
        urls = super().get_urls()

        extra_urls = [
            path(
                "translate/<int:id>/",
                self.admin_site.admin_view(
                    ArticleAdminTranslateView.as_view(),
                ),
                {"model_admin": self},
                name="lotus_article_translate_original",
            )
        ]

        return extra_urls + urls


# Registering interface to model
admin.site.register(Article, ArticleAdmin)
