from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.utils.translation import gettext as _

from ..models import Article


class ArticleIndexView(ListView):
    """
    Paginated list of articles
    """
    model = Article
    template_name = "lotus/article/list.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "article_list"

    def get_queryset(self):
        q = self.model.objects.get_for_lang(self.request.LANGUAGE_CODE)

        if not self.request.GET.get("admin") or not self.request.user.is_staff:
            q = q.get_published()

        if not self.request.user.is_authenticated:
            q = q.filter(private=False)

        return q.order_by(*self.model.COMMON_ORDER_BY)


class ArticleDetailView(DetailView):
    """
    Article detail
    """
    model = Article
    pk_url_kwarg = "article_pk"
    template_name = "lotus/article/detail.html"
    context_object_name = "article_object"

    def get_queryset(self):
        """
        Get the base queryset which may include the basic publication filter
        depending admin mode.

        Admin mode is enabled if url have "admin" argument and user is staff member.

        If Admin mode is disabled publication criterias are applied as lookups.

        Also apply lookup for "private" mode for non authenticated users.
        """
        q = self.model.objects.get_for_lang(self.request.LANGUAGE_CODE)

        if not self.request.GET.get("admin") or not self.request.user.is_staff:
            q = q.get_published()

        if not self.request.user.is_authenticated:
            q = q.filter(private=False)

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
