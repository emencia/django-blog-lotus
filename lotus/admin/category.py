from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext_lazy as _

from smart_media.admin import SmartModelAdmin

from ..forms import CategoryAdminForm
from ..models import Category
from ..views.admin import CategoryAdminTranslateView, CategoryAdminTreeView

from ..admin_filters import LanguageListFilter, TranslationStateListFilter


LANGUAGE_NAMES = dict(settings.LANGUAGES)
"""
Shortcut to get setting as a dict
"""


@admin.register(Category)
class CategoryAdmin(SmartModelAdmin):
    """
    NOTE: Usage of TreeAdmin is not really working because queryset follows the order
    on title instead of path + title. This lead to broken tree display. Also we don't
    want of drag-n-drop that will fails/messes with languages.
    """
    form = CategoryAdminForm
    list_display = (
        "title",
        "language_name",
        "is_original",
        "get_parent",
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
        "lead",
        "description",
    ]
    fieldsets = (
        (
            None, {
                "fields": (
                    "_position",
                    "_ref_node_id",
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
                    "template",
                )
            }
        ),
        (
            _("Content"), {
                "fields": (
                    ("cover", "cover_alt_text"),
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

    class Media:
        css = settings.LOTUS_ADMIN_CATEGORY_ASSETS.get("css", None)
        js = settings.LOTUS_ADMIN_CATEGORY_ASSETS.get("js", None)

    def language_name(self, obj):
        if obj.language in LANGUAGE_NAMES:
            return LANGUAGE_NAMES[obj.language]
        return "{} (disabled)".format(obj.language)
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

    def get_parent(self, obj):
        return obj.get_parent()
    get_parent.short_description = _("parent")

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
            ),
            path(
                "tree/",
                self.admin_site.admin_view(
                    CategoryAdminTreeView.as_view(),
                ),
                {"model_admin": self},
                name="lotus_category_tree",
            ),
        ]

        return extra_urls + urls
