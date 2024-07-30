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
        q = self.model.objects.get_for_lang(self.get_language_code())

        return q.order_by(*self.model.COMMON_ORDER_BY)


class CategoryDetailView(BaseBreadcrumbMixin, ArticleFilterAbstractView,
                         SingleObjectMixin, ListView):
    """
    Category detail and its related article list.
    """
    model = Category
    listed_model = Article
    template_name = "lotus/category/detail.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "category_object"
    slug_url_kwarg = "slug"
    pk_url_kwarg = None
    crumb_title = None  # No usage since title depends from object
    crumb_urlname = "lotus:category-detail"
    lotus_stage = "categories"

    @property
    def crumbs(self):
        details_kwargs = {
            "slug": self.object.slug,
        }

        return [
            (CategoryIndexView.crumb_title, reverse(
                CategoryIndexView.crumb_urlname
            )),
            (self.object.title, reverse(self.crumb_urlname, kwargs=details_kwargs)),
        ]

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


# WARNING: Temporarily during development
from django.http import HttpResponse
from django.views.generic import View
class CategoryTreeView(LotusContextStage, PreviewModeMixin, LanguageMixin, View):
    """
    Tree of categories in plain/text format.

    Categories are properly filtered on language since anyway we can't display a tree
    of all categories with mixed languages.
    """
    model = Category
    lotus_stage = "categories"

    def get_queryset(self):
        """
        Build queryset base with language filtering to list categories.
        """
        q = self.model.objects.get_for_lang(self.get_language_code())

        # NOTE: Deprecated usage of ``*self.model.COMMON_ORDER_BY`` in order_by since
        # treebeard is used to add new node sorted on title, so path resolution should
        # be identical to the previous behavior before treebeard implementation.
        return q.order_by("path")

    def get_output(self):
        """
        Build output items
        """
        title = "For language '{}'".format(self.get_language_code())

        output = [
            title,
            "=" * len(title),
            "",
        ]

        items = Category.get_annotated_list_qs(self.get_queryset())
        row = "{indent}{name}"
        for obj, data in items:
            indent = ("    " * data["level"]) + "└── "
            output.append(row.format(
                indent=indent if data["level"] > 0 else "",
                name=obj.slug,
            ))

        return output

    def get(self, request):
        """
        Return built JSON content from features.
        """
        return HttpResponse(
            "\n".join(self.get_output()),
            content_type="text/plain; charset=utf-8"
        )
