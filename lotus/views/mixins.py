from django.utils import timezone


class NoOperationBreadcrumMixin:
    """
    A dummy and empty mixin to use when 'view_breadcrumbs' is not available.
    """
    pass


class AdminModeMixin:
    """
    A mixin to contain the logic for admin mode and add a context variable
    ``preview_mode``.

    Admin mode is only allowed for staff users which use URL with a specific argument
    as defined in ``PreviewModeMixin.adminmode_argument_name``.

    Like a staff user can is allowed for admin mode if it use URL with argument
    ``?admin=1`` but not without argument even if it's a superuser. Other user kind and
    anonymous are never allowed for admin mode.

    The admin mode is essentially used to not filter queryset with publication
    criterias.
    """
    # TODO: This should depend from a settings since they are pretty common words in
    # the app world so it could be changed to avoid conflicts.
    adminmode_argument_name = "admin"
    adminmode_context_name = "admin_mode"

    def allowed_preview_mode(self, request):
        """
        Return if admin mode is allowed or not.
        """
        return not(
            not self.request.GET.get(self.adminmode_argument_name) or
            not self.request.user.is_staff
        )

    def get_context_data(self, **kwargs):
        """
        Expose the date "now" used for publication filter.
        """
        context = super().get_context_data(**kwargs)
        context["admin_mode"] = self.allowed_preview_mode(self.request)

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

        Depend on ``allowed_preview_mode`` method as implemented in ``AdminModeMixin``
        which manage admin mode.

        Arguments:
            queryset (django.db.models.QuerySet): Base queryset to start on.
            language (string): Language code to filter on.

        Returns:
            django.db.models.QuerySet: Improved queryset with required filtering
            lookups.
        """
        self.target_date = timezone.now()

        # Admin request have no restriction on date so it can return draft or future
        # publications
        if self.allowed_preview_mode(self.request):
            queryset = queryset.get_for_lang(language=language)
        # Default request for common user
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
