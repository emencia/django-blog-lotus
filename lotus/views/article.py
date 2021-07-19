from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.utils.translation import gettext as _
from django.utils import timezone

from ..models import Article


class ArticleFilterMixin:
    """
    A mixin to share Article filtering.
    """
    def apply_article_lookups(self, queryset, language):
        """
        Apply publication and language lookups to given queryset.

        Also this will set a ``self.target_date`` attribute to store the date checked
        against as a reference for further usage (like in ``get_context_data``).

        Arguments:
            queryset (django.db.models.QuerySet): Base queryset to start on.
            language (string): Language code to filter on.

        Returns:
            django.db.models.QuerySet: Improved queryset with required filtering
            lookups.
        """
        self.target_date = timezone.now()

        if (
            not self.request.GET.get("admin") or
            not self.request.user.is_staff
        ):
            queryset = queryset.get_published(
                target_date=self.target_date,
                language=language,
            )
        else:
            queryset = queryset.get_for_lang(language=language)

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


class ArticleIndexView(ArticleFilterMixin, ListView):
    """
    Paginated list of articles.
    """
    model = Article
    template_name = "lotus/article/list.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "article_list"

    def get_queryset(self):
        q = self.apply_article_lookups(self.model.objects, self.request.LANGUAGE_CODE)

        return q.order_by(*self.model.COMMON_ORDER_BY)


class ArticleDetailView(ArticleFilterMixin, DetailView):
    """
    Article detail.
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
