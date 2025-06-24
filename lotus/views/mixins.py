from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..exceptions import Http500
from ..lookups import LookupBuilder
from ..utils.language import get_language_code


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
        Expose the preview mode state to template.
        """
        context = super().get_context_data(**kwargs)
        context[settings.LOTUS_PREVIEW_VARNAME] = self.allowed_preview_mode(
            self.request
        )

        return context


class ArticleFilterMixin(LookupBuilder):
    """
    A mixin to share Article filtering.

    .. TODO::
        Rewrite docstrings since allowed_preview_mode deps is not required
        anymore, only optional.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO:  Documentate this new attribute and why it exists here instead of
        # previously in method build/apply lookup
        self.target_date = timezone.now()

    def is_for_authenticated_user(self):
        if not hasattr(self, "request"):
            return False

        return self.request.user.is_authenticated

    def build_article_lookups(self, language=None, prefix=None):
        """
        Build complex lookups to apply common publication criterias.

        Also set a ``self.target_date`` attribute to store the date checked
        against as a reference for further usage (like in ``get_context_data``).

        Depends on ``allowed_preview_mode`` method as implemented in
        ``PreviewModeMixin`` (that manage preview mode) and the queryset must be for a
        model with a manager which implement ``get_for_lang`` and ``get_published``
        methods.

        Keyword Arguments:
            language (string): Language code to filter on.

        Returns:
            tuple: The lookups to give to a queryset filter.
        """
        lookups = []
        prefix = prefix or ""

        # Define target_date attribute if it does not exists yet
        if not hasattr(self, "target_date"):
            self.target_date = timezone.now()

        # Check for enabled preview mode
        if (
            language and
            hasattr(self, "allowed_preview_mode") and
            self.allowed_preview_mode(self.request)
        ):
            lookups.extend(
                self.build_language_conditions(language, prefix=prefix)
            )
        # Default request instead
        else:
            lookups.extend(
                self.build_publication_conditions(
                    target_date=None,
                    language=language,
                    private=None if self.is_for_authenticated_user() else False,
                    prefix=prefix,
                )
            )

        return tuple(lookups)

    def apply_article_lookups(self, queryset, language=None):
        """
        Apply publication and language lookups to given queryset.

        This will set a ``self.target_date`` attribute to store the date checked
        against as a reference for further usage (like in ``get_context_data``).

        The queryset must be for a model with a manager which implement
        ``get_for_lang`` and ``get_published`` methods. This support also
        ``allowed_preview_mode`` method as implemented in ``PreviewModeMixin``
        (that manage preview mode) if it is available.

        Arguments:
            queryset (django.db.models.QuerySet): Base queryset to start on.

        Keyword Arguments:
            language (string): Language code to filter on.

        Returns:
            django.db.models.QuerySet: Improved queryset with required filtering
            lookups.
        """
        # Define target_date attribute if it does not exists yet
        if not hasattr(self, "target_date"):
            self.target_date = timezone.now()

        # Check for enabled preview mode which allows to ignore publication rules, only
        # care about language
        if (
            hasattr(self, "allowed_preview_mode") and
            self.allowed_preview_mode(self.request)
        ) and language:
            queryset = queryset.get_for_lang(language=language)
        # Default request instead
        else:
            queryset = queryset.get_published(
                target_date=self.target_date,
                language=language,
                private=None if self.is_for_authenticated_user() else False,
            )

        return queryset


class LanguageMixin:
    """
    A mixin to provide very common logic related to language.
    """
    def get_language_code(self):
        """
        Shortand to ``get_language_code`` function that already give the request object.

        .. Warning::
            This should not be used in view code before request attribute has been set.

        Returns:
            string: Language code retrieved either from request object or settings.
        """
        return get_language_code(self.request)


class LotusContextStage:
    """
    Mixin to inject Lotus stage into view context.

    Lotus stage is commonly used for Lotus navigation, it just indicates where a view
    is located from main Lotus content type views (Article, Author, Category, ..).

    Views which inherits from this mixin should set view attribute ``lotus_stage`` to
    a main content type in lowercase like ``articles``, ``authors``, ``category``.

    The default stage value is ``None``.

    Finally, the Lotus stage is just an helper for basic navigation like in a menu to
    highlight corresponding item. There is no code which use it so it can be ignored
    from custom Lotus implementation.
    """
    lotus_stage = None

    def get_lotus_stage(self):
        return self.lotus_stage

    def get_context_data(self, **kwargs):
        """
        Expose the date "now" used for publication filter.
        """
        context = super().get_context_data(**kwargs)
        context["lotus_stage"] = self.get_lotus_stage()
        return context


class ArticleFilterAbstractView(LotusContextStage, ArticleFilterMixin,
                                PreviewModeMixin, LanguageMixin):
    """
    Abstract class which gather all the classes needed to implement filtering on
    criterias.
    """
    def get_context_data(self, **kwargs):
        """
        Expose the date "now" used for publication filter and the article filtering.
        function
        """
        context = super().get_context_data(**kwargs)
        context["article_filter_func"] = getattr(self, "apply_article_lookups")
        context["lotus_now"] = getattr(self, "target_date")
        return context


class TemplateFromObjectMixin:
    """
    A mixin to get the template to render from the object attribute ``template``.

    It is intended to override the template mechanism from ``TemplateResponseMixin`` and
    for a view which have an attribute ``object`` where to find the attribute
    ``template``.
    """
    def get_template_names(self):
        """
        Overrides the original method to get the template name from the object.

        Returns:
            list: List of template name as expected by the Django mechanism but the
            list will always have an unique item.
        """
        if not hasattr(self, "object"):
            raise Http500(
                _("TemplateFromObjectMixin usage requires an attribute 'object'.")
            )

        return [self.object.template]
