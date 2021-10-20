from django.conf import settings
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from ..models import Article, Author
from .mixins import AdminModeMixin, ArticleFilterMixin


class AuthorIndexView(ListView):
    """
    List of authors which have contributed at least to one article.
    """
    model = Author
    template_name = "lotus/author/list.html"
    paginate_by = settings.LOTUS_AUTHOR_PAGINATION
    context_object_name = "author_list"

    def get_queryset(self):
        q = self.model.lotus_objects.get_active(language=self.request.LANGUAGE_CODE)

        return q.order_by(*self.model.COMMON_ORDER_BY)


class AuthorDetailView(ArticleFilterMixin, AdminModeMixin, SingleObjectMixin, ListView):
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
            self.request.LANGUAGE_CODE,
        )

        return q.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get(self, request, *args, **kwargs):
        # Try to get Author object
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        # Let the ListView mechanics manage list pagination from given queryset
        return super().get(request, *args, **kwargs)
