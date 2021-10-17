"""
Category admin interface
"""
from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..forms import CategoryAdminForm
from ..models import Category

from .translated import LanguageListFilter


# Shortcut to get setting as a dict
LANGUAGE_NAMES = dict(settings.LANGUAGES)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = (
        "title",
        "language_name",
        "article_count",
    )
    list_filter = (
        LanguageListFilter,
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

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _("articles")
