from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .choices import get_language_choices


class LanguageListFilter(admin.SimpleListFilter):
    """
    Add Human-readable language title as defined in LANGUAGES setting.
    """
    title = _("language")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "lang"

    def lookups(self, request, model_admin):
        """
        Build choices from available languages.
        """
        return get_language_choices()

    def queryset(self, request, queryset):
        """
        Use given language if any
        """
        if self.value():
            return queryset.filter(language=self.value())


class TranslationStateListFilter(admin.SimpleListFilter):
    """
    Filtering original article and translations.
    """
    title = _("translation state")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "translation_state"

    def lookups(self, request, model_admin):
        return (
            ("original", _("Is an original")),
            ("translation", _("Is a translation")),
        )

    def queryset(self, request, queryset):
        if self.value() == "original":
            return queryset.filter(original__isnull=True)

        if self.value() == "translation":
            return queryset.exclude(original__isnull=True)


class PublicationFilter(admin.SimpleListFilter):
    """
    Filter on article publication state.
    """
    title = _("publication state")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "is_published"

    def lookups(self, request, model_admin):
        """
        Build choices from available languages.
        """
        return (
            ("true", _("Is published")),
            ("false", _("Is not published")),
        )

    def queryset(self, request, queryset):
        """
        Filter on published or unpublished article depending value is true or false.
        """
        if self.value() == "true":
            return queryset.get_published()

        if self.value() == "false":
            return queryset.get_unpublished()
