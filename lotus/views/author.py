from django.conf import settings
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse

from ..models import Article, Author
from .mixins import (
    ArticleFilterAbstractView,
    LanguageMixin,
    LotusContextStage,
    PreviewModeMixin,
)

try:
    from view_breadcrumbs import BaseBreadcrumbMixin
except ImportError:
    from .mixins import NoOperationBreadcrumMixin as BaseBreadcrumbMixin


class AuthorIndexView(BaseBreadcrumbMixin, LotusContextStage, PreviewModeMixin,
                      LanguageMixin, ListView):
    """
    List of authors which have contributed at least to one article.
    """
    model = Author
    template_name = "lotus/author/list.html"
    paginate_by = settings.LOTUS_AUTHOR_PAGINATION
    context_object_name = "author_list"
    crumb_title = settings.LOTUS_CRUMBS_TITLES["author-index"]
    crumb_urlname = "lotus:author-index"
    lotus_stage = "authors"

    @property
    def crumbs(self):
        return [
            (self.crumb_title, reverse(self.crumb_urlname)),
        ]

    def get_queryset(self):
        q = self.model.lotus_objects.get_active(
            language=self.get_language_code(),
            private=None if self.request.user.is_authenticated else False,
        )

        return q.order_by(*self.model.COMMON_ORDER_BY)


class AuthorDetailView(BaseBreadcrumbMixin, ArticleFilterAbstractView,
                       SingleObjectMixin, ListView):
    """
    Author detail and its related article list.

    Opposed to article or category listing, this one list objects for language from
    request, not from the author language since it dont have one.
    """
    model = Author
    listed_model = Article
    template_name = "lotus/author/detail.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "author_object"
    slug_field = "username"
    slug_url_kwarg = "username"
    pk_url_kwarg = None
    crumb_title = None  # No usage since title depends from object
    crumb_urlname = "lotus:author-detail"
    lotus_stage = "authors"

    @property
    def crumbs(self):
        details_kwargs = {
            "username": self.object.username,
        }

        return [
            (AuthorIndexView.crumb_title, reverse(
                AuthorIndexView.crumb_urlname
            )),
            (str(self.object), reverse(self.crumb_urlname, kwargs=details_kwargs)),
        ]

    def get_queryset_for_object(self):
        """
        Build queryset base to get Author.
        """
        return self.model.objects

    def get_queryset(self):
        """
        Build queryset base to list Author articles.

        Depend on "self.object" to list the Author related objects.
        """
        q = self.apply_article_lookups(
            self.object.articles,
            self.get_language_code(),
        )

        return q.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get(self, request, *args, **kwargs):
        # Try to get Author object
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        # Let the ListView mechanics manage list pagination from given queryset
        return super().get(request, *args, **kwargs)
