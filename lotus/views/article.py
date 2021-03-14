from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView


from ..models import Article


class ArticleIndexView(ListView):
    """
    List of categories
    """
    model = Article
    queryset = Article.objects.order_by('title')
    template_name = "lotus/category_index.html"
    paginate_by = settings.BLOG_PAGINATION


class ArticleDetailView(DetailView):
    """
    Article detail
    """
    pk_url_kwarg = "article_pk"
    template_name = "lotus/article_detail.html"
    context_object_name = "article_object"
