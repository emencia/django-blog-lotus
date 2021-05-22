from django.conf import settings
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from ..models import Category


class CategoryIndexView(ListView):
    """
    List of categories
    """
    model = Category
    queryset = Category.objects.order_by("title")
    template_name = "lotus/category/index.html"
    paginate_by = settings.LOTUS_CATEGORY_PAGINATION
    context_object_name = "category_list"



class CategoryDetailView(SingleObjectMixin, ListView):
    """
    Category detail and its related article list
    """
    pk_url_kwarg = "category_pk"
    template_name = "lotus/category/detail.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "category_object"

    def get_queryset(self):
        return self.object.article_set.order_by("title")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Category.objects.all())

        return super().get(request, *args, **kwargs)
