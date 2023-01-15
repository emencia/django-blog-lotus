from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext_lazy as _

from smart_media.admin import SmartModelAdmin

from ..forms import CategoryAdminForm
from ..models import Category
from ..views.admin import CategoryAdminTranslateView

from .translated import LanguageListFilter, TranslationStateListFilter


LANGUAGE_NAMES = dict(settings.LANGUAGES)
"""
Shortcut to get setting as a dict
"""


@admin.register(Category)
class CategoryAdmin(SmartModelAdmin):
    form = CategoryAdminForm
    list_display = (
        "title",
        "language_name",
        "is_original",
        "article_count",
    )
    list_filter = (
        LanguageListFilter,
        TranslationStateListFilter,
    )
    list_per_page = 50
    prepopulated_fields = {
        "slug": ("title",),
    }
    ordering = Category.COMMON_ORDER_BY
    search_fields = [
        "title",
    ]
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
            _("Content"), {
                "fields": (
                    "cover",
                    "description",
                )
            }
        ),
        (
            _("SEO"), {
                "fields": (
                    "lead",
                )
            }
        ),
    )

    def language_name(self, obj):
        return LANGUAGE_NAMES[obj.language]
    language_name.short_description = _("language")
    language_name.admin_order_field = "language"

    def is_original(self, obj):
        """
        Check article is an original or a translation.
        """
        return obj.original is None
    is_original.short_description = _("original")
    is_original.boolean = True

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _("articles")

    def get_urls(self):
        """
        Set some additional custom admin views
        """
        urls = super().get_urls()

        extra_urls = [
            path(
                "translate/<int:id>/",
                self.admin_site.admin_view(
                    CategoryAdminTranslateView.as_view(),
                ),
                {"model_admin": self},
                name="lotus_category_translate_original",
            )
        ]

        return extra_urls + urls
