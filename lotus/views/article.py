from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

try:
    from view_breadcrumbs import BaseBreadcrumbMixin
except ImportError:
    from .mixins import NoOperationBreadcrumMixin as BaseBreadcrumbMixin

from ..models import Article
from .mixins import AdminModeMixin, ArticleFilterMixin


class ArticleIndexView(BaseBreadcrumbMixin, ArticleFilterMixin, AdminModeMixin,
                       ListView):
    """
    Paginated list of articles.
    """
    model = Article
    template_name = "lotus/article/list.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "article_list"
    crumb_title = _("Articles")
    crumb_urlname = "lotus:article-index"

    @property
    def crumbs(self):
        return [
            (self.crumb_title, reverse(self.crumb_urlname)),
        ]

    def get_queryset(self):
        q = self.apply_article_lookups(self.model.objects, self.request.LANGUAGE_CODE)

        return q.order_by(*self.model.COMMON_ORDER_BY)


class ArticleDetailView(BaseBreadcrumbMixin, ArticleFilterMixin, AdminModeMixin,
                        DetailView):
    """
    Article detail.
    """
    model = Article
    pk_url_kwarg = "article_pk"
    template_name = "lotus/article/detail.html"
    context_object_name = "article_object"
    crumb_title = None  # No usage since title depends from object
    crumb_urlname = "lotus:article-detail"

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
        depending admin mode.

        Admin mode is enabled if url have "admin" argument and user is staff member.

        If Admin mode is disabled publication criterias are applied as lookups.

        Also apply lookup for "private" mode for non authenticated users.
        """
        q = self.apply_article_lookups(self.model.objects, self.request.LANGUAGE_CODE)

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
