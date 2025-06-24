from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext_lazy as _

from smart_media.admin import SmartModelAdmin

from ..forms import ArticleAdminForm
from ..models import Article
from ..views.admin import ArticleAdminTranslateView

from ..admin_filters import (
    LanguageListFilter,
    PublicationFilter,
    TranslationStateListFilter,
)


LANGUAGE_NAMES = dict(settings.LANGUAGES)
"""
Shortcut to get setting as a dict
"""


@admin.register(Article)
class ArticleAdmin(SmartModelAdmin):
    form = ArticleAdminForm
    list_display = (
        "title",
        "is_published",
        "publish_datetime",
        "language_name",
        "is_original",
        "pinned",
        "featured",
        "last_update",
        "private",
    )
    list_filter = (
        LanguageListFilter,
        TranslationStateListFilter,
        PublicationFilter,
        "pinned",
        "featured",
        "private",
        "categories",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    ordering = Article.COMMON_ORDER_BY
    search_fields = [
        "title",
        "seo_title",
        "lead",
        "introduction",
        "content",
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
                    "language",
                    "original",
                )
            }
        ),
        (
            _("Parameters"), {
                "fields": (
                    "status",
                    "template",
                    "featured",
                    "pinned",
                    "private",
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
                    ("cover", "cover_alt_text"),
                    "introduction",
                    ("image", "image_alt_text"),
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
                    "album",
                    "categories",
                    "tags",
                    "authors",
                    "related",
                )
            }
        ),
    )

    class Media:
        css = settings.LOTUS_ADMIN_ARTICLE_ASSETS.get("css", None)
        js = settings.LOTUS_ADMIN_ARTICLE_ASSETS.get("js", None)

    def language_name(self, obj):
        """
        Return humanized name for object language code.
        """
        if obj.language in LANGUAGE_NAMES:
            return LANGUAGE_NAMES[obj.language]
        return "{} (disabled)".format(obj.language)
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
        return obj.is_published()
    is_published.short_description = _("published")
    is_published.boolean = True

    def is_original(self, obj):
        """
        Check article is an original or a translation.
        """
        return obj.original is None
    is_original.short_description = _("original")
    is_original.boolean = True

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
