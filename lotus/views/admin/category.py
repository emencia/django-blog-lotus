from ...models import Category

from .mixins import AdminTranslateView


class CategoryAdminTranslateView(AdminTranslateView):
    """
    Display a form to select a language to translate a category to.
    """
    model = Category
    template_name = "admin/lotus/category/translate_original.html"
