from django.conf import settings
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from ..models import Article, Category
from .article import ArticleFilterMixin


class CategoryIndexView(ListView):
    """
    List of categories
    """
    model = Category
    template_name = "lotus/category/list.html"
    paginate_by = settings.LOTUS_CATEGORY_PAGINATION
    context_object_name = "category_list"

    def get_queryset(self):
        q = self.model.objects.get_for_lang(self.request.LANGUAGE_CODE)

        return q.order_by(*self.model.COMMON_ORDER_BY)


class CategoryDetailView(ArticleFilterMixin, SingleObjectMixin, ListView):
    """
    Category detail and its related article list

    TODO:
        To finish when new model test has been added about getting category related
        articles.
    """
    pk_url_kwarg = "category_pk"
    model = Category
    listed_model = Article
    template_name = "lotus/category/detail.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "category_object"
    slug_url_kwarg = 'slug'
    pk_url_kwarg = None

    def get_queryset_for_object(self):
        """
        Used to get Category.
        """
        q = self.model.objects.get_for_lang(self.request.LANGUAGE_CODE)

        return q

    def get_queryset(self):
        """
        Used for article listing.

        Depend on "self.object" to list Category related objects.
        """
        q = self.object.get_articles(ordered=False)

        q = self.apply_article_lookups(q)

        return q.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        return super().get(request, *args, **kwargs)
