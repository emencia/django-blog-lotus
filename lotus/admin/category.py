# -*- coding: utf-8 -*-
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
        "is_translation",
        "article_count",
        "cover",
    )
    list_filter = (
        LanguageListFilter,
    )
    list_per_page = 50
    prepopulated_fields = {
        "slug": ("title",),
    }
    ordering = (
        "title",
        "language",
    )
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
                    "lead",
                    "cover",
                    "description",
                )
            }
        ),
    )

    def is_translation(self, obj):
        return not(obj.original is None)
    is_translation.short_description = _("translation")
    is_translation.boolean = True

    def language_name(self, obj):
        return LANGUAGE_NAMES[obj.language]
    language_name.short_description = _("language")

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _("articles")
