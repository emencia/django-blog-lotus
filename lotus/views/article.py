from django.conf import settings
from django.http import Http404, HttpResponseForbidden
from django.views.generic import DetailView, ListView
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from ..models import Article
from .mixins import ArticleFilterAbstractView, TemplateFromObjectMixin

try:
    from view_breadcrumbs import BaseBreadcrumbMixin
except ImportError:
    from .mixins import NoOperationBreadcrumMixin as BaseBreadcrumbMixin


class ArticleIndexView(BaseBreadcrumbMixin, ArticleFilterAbstractView, ListView):
    """
    Paginated list of articles.
    """
    model = Article
    template_name = "lotus/article/list.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "article_list"
    crumb_title = settings.LOTUS_CRUMBS_TITLES["article-index"]
    crumb_urlname = "lotus:article-index"
    lotus_stage = "articles"

    @property
    def crumbs(self):
        return [
            (self.crumb_title, reverse(self.crumb_urlname)),
        ]

    def get_queryset(self):
        q = self.apply_article_lookups(self.model.objects, self.get_language_code())

        return q.order_by(*self.model.COMMON_ORDER_BY)


class ArticleDetailView(BaseBreadcrumbMixin, ArticleFilterAbstractView,
                        TemplateFromObjectMixin, DetailView):
    """
    Article detail.
    """
    model = Article
    pk_url_kwarg = "article_pk"
    template_name = None
    context_object_name = "article_object"
    crumb_title = None  # No usage since title depends from object
    crumb_urlname = "lotus:article-detail"
    lotus_stage = "articles"

    @property
    def crumbs(self):
        details_kwargs = {
            "year": self.object.publish_date.year,
            "month": self.object.publish_date.month,
            "day": self.object.publish_date.day,
            "slug": self.object.slug,
        }

        return [
            (ArticleIndexView.crumb_title, reverse(
                ArticleIndexView.crumb_urlname
            )),
            (self.object.title, reverse(self.crumb_urlname, kwargs=details_kwargs)),
        ]

    def get_queryset(self):
        """
        Get the base queryset which may include the basic publication filter
        depending preview mode.

        Preview mode is enabled from a flag in session and only for staff user. If it is
        disabled publication criterias are applied on lookups.

        Also apply lookup against "preview" mode.
        """
        q = self.apply_article_lookups(self.model.objects, self.get_language_code())

        return q

    def get_object(self, queryset=None):
        """
        Apply the right filters to get the article object.
        """
        # Use a custom queryset if provided
        if queryset is None:
            queryset = self.get_queryset()

        # Add proper filters to get object respecting URL arguments
        q_kwargs = {
            "publish_date__year": self.kwargs.get("year"),
            "publish_date__month": self.kwargs.get("month"),
            "publish_date__day": self.kwargs.get("day"),
            "slug": self.kwargs.get("slug"),
        }
        queryset = queryset.filter(**q_kwargs)

        # Try to get article object from given lookups
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        return obj


class PreviewArticleDetailView(ArticleDetailView):
    """
    TODO: Should force set the context var for preview mode at True without to tamper
    session so the user session is still in its current state but it can preview.
    """
    def allowed_preview_mode(self, request):
        """
        Force preview mode for querysets.
        """
        return True

    def get_context_data(self, **kwargs):
        """
        Force preview mode in context (without tampering preview mode in session).

        .. Todo::
            Control user staff with a custom permission to use this ?
        """
        context = super().get_context_data(**kwargs)
        context[settings.LOTUS_PREVIEW_VARNAME] = True

        return context

    def get(self, request, *args, **kwargs):
        """
        Ensure that user is allowed to use this view.
        """
        if not self.request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to be here.")

        return super().get(request, *args, **kwargs)
