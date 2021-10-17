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

    def choices(self, changelist):
        """
        Hack the filter list to change the default name to match this specific filter
        behavior.
        """
        choices = list(super().choices(changelist))
        choices[0]["display"] = _("Default language")

        return choices

    def lookups(self, request, model_admin):
        """
        Add again the "All" entry but with a special keyword "all" to use to select the
        right queryset.
        """
        base_choices = list(get_language_choices())

        return [('all', _('All'))] + base_choices

    def queryset(self, request, queryset):
        """
        Use the default language for default queryset (with no URL argument) or
        return article queryset for all language (if ``all`` argument is given) or
        return article queryset filtered on given language code (from given argument).
        """
        if self.value() and  self.value() == "all":
            return queryset.filter()
        elif self.value():
            return queryset.filter(language=self.value())
        else:
            return queryset.filter(language=get_language_default())
