from django.conf import settings
from django.utils import timezone


class NoOperationBreadcrumMixin:
    """
    A dummy and empty mixin to use when 'view_breadcrumbs' is not available.
    """
    pass


class PreviewModeMixin:
    """
    A mixin to contain the logic for preview mode and add a context variable
    ``preview_mode``.

    Preview mode is only allowed for staff users which use URL with a specific argument
    as defined in setting ``LOTUS_PREVIEW_KEYWORD``.

    A staff user is only allowed for preview mode if its session have the right item set
    to ``True`` exactly.

    The preview mode is essentially used to not filter queryset with publication
    criterias.
    """
    def allowed_preview_mode(self, request):
        """
        Return if preview mode is enabled or not.
        """
        if not self.request.user.is_staff:
            return False

        return self.request.session.get(settings.LOTUS_PREVIEW_KEYWORD, None) is True

    def get_context_data(self, **kwargs):
        """
        Expose the preview mode state.
        """
        context = super().get_context_data(**kwargs)
        context[settings.LOTUS_PREVIEW_VARNAME] = self.allowed_preview_mode(
            self.request
        )

        return context


class ArticleFilterMixin:
    """
    A mixin to share Article filtering.
    """
    def apply_article_lookups(self, queryset, language):
        """
        Apply publication and language lookups to given queryset.

        Also this will set a ``self.target_date`` attribute to store the date checked
        against as a reference for further usage (like in ``get_context_data``).

        Depend on ``allowed_preview_mode`` method as implemented in ``PreviewModeMixin``
        which manage preview mode.

        Arguments:
            queryset (django.db.models.QuerySet): Base queryset to start on.
            language (string): Language code to filter on.

        Returns:
            django.db.models.QuerySet: Improved queryset with required filtering
            lookups.
        """
        self.target_date = timezone.now()

        # Check for enabled preview mode
        if self.allowed_preview_mode(self.request):
            queryset = queryset.get_for_lang(language=language)
        # Default request instead
        else:
            queryset = queryset.get_published(
                target_date=self.target_date,
                language=language,
            )

        # Avoid anonymous to see private content
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(private=False)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Expose the date "now" used for publication filter.
        """
        context = super().get_context_data(**kwargs)
        context["lotus_now"] = self.target_date
        return context
