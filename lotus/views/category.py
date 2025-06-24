from django.conf import settings
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse

from ..models import Article, Category

from .mixins import (
    ArticleFilterAbstractView,
    LanguageMixin,
    LotusContextStage,
    PreviewModeMixin,
    TemplateFromObjectMixin,
)

try:
    from view_breadcrumbs import BaseBreadcrumbMixin
except ImportError:
    from .mixins import NoOperationBreadcrumMixin as BaseBreadcrumbMixin


class CategoryIndexView(BaseBreadcrumbMixin, LotusContextStage, PreviewModeMixin,
                        LanguageMixin, ListView):
    """
    List of categories
    """
    model = Category
    template_name = "lotus/category/list.html"
    paginate_by = settings.LOTUS_CATEGORY_PAGINATION
    context_object_name = "category_list"
    crumb_title = settings.LOTUS_CRUMBS_TITLES["category-index"]
    crumb_urlname = "lotus:category-index"
    lotus_stage = "categories"

    @property
    def crumbs(self):
        return [
            (self.crumb_title, reverse(self.crumb_urlname)),
        ]

    def get_queryset(self):
        """
        Build queryset base with language filtering to list categories.
        """
        q = self.model.objects.filter(depth=1).get_for_lang(self.get_language_code())

        return q.order_by(*self.model.COMMON_ORDER_BY)


class CategoryDetailView(BaseBreadcrumbMixin, ArticleFilterAbstractView,
                         TemplateFromObjectMixin, SingleObjectMixin, ListView):
    """
    Category detail and its related article list.
    """
    model = Category
    listed_model = Article
    template_name = None
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "category_object"
    slug_url_kwarg = "slug"
    pk_url_kwarg = None
    crumb_title = None  # No usage since title depends from object
    crumb_urlname = "lotus:category-detail"
    lotus_stage = "categories"

    @property
    def crumbs(self):
        # Start with previous paths
        crumbs = [(
            CategoryIndexView.crumb_title,
            reverse(CategoryIndexView.crumb_urlname)
        )]

        # Append ancestors
        if not settings.LOTUS_CATEGORY_SHORT_CRUMBS and self.object.depth > 1:
            queryset = self.object.get_ancestors().filter(
                language=self.get_language_code()
            )
            for ancestor in queryset:
                crumbs.append((
                    ancestor.title,
                    reverse(self.crumb_urlname, kwargs={"slug": ancestor.slug})
                ))

        # Last item is the current category
        crumbs.append((
            self.object.title,
            reverse(self.crumb_urlname, kwargs={"slug": self.object.slug})
        ))

        return crumbs

    def get_queryset_for_object(self):
        """
        Build queryset base with language filtering to get Category.
        """
        return self.model.objects.get_for_lang(self.get_language_code())

    def get_queryset(self):
        """
        Build queryset base to list Category articles.

        Depend on "self.object" to list the Category related objects filtered on its
        language.
        """
        q = self.apply_article_lookups(
            self.object.articles,
            self.object.language,
        )

        return q.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get(self, request, *args, **kwargs):
        # Try to get Category object
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        # Let the ListView mechanics manage list pagination from given queryset
        return super().get(request, *args, **kwargs)
