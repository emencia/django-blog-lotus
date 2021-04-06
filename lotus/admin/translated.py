from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..choices import get_language_choices, get_language_default


class LanguageListFilter(admin.SimpleListFilter):
    """
    Add Human-readable language title as defined in LANGUAGES setting.
    """
    title = _("language")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "lang"

    def lookups(self, request, model_admin):
        return get_language_choices()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(language=self.value())
