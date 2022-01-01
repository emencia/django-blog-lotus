from ...models import Article

from .mixins import AdminTranslateView


class ArticleAdminTranslateView(AdminTranslateView):
    """
    Display a form to select a language to translate an article to.
    """
    model = Article
    template_name = "admin/lotus/article/translate_original.html"
