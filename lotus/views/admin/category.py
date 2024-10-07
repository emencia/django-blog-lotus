from django.conf import settings
from django.forms.widgets import Media
from django.http import Http404
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

from ...models import Category
from .mixins import AdminTranslateView, CustomLotusAdminContext


class CategoryAdminTranslateView(AdminTranslateView):
    """
    Display a form to select a language to translate a category to.
    """
    model = Category
    template_name = "admin/lotus/category/translate_original.html"


class CategoryAdminTreeView(CustomLotusAdminContext, TemplateView):
    """
    An admin view to list a tree of categories.

    Since it is a tree this view can't enable pagination because it is not safe to
    cut a tree in multiple pages.
    """
    model = Category
    template_name = "admin/lotus/category/tree.html"
    language_kwarg = "lang"

    def get_view_media(self):
        """
        Get Media object for Category admin views static files.

        Returns:
            django.forms.widgets.Media: Media object.
        """
        return Media(
            css=settings.LOTUS_ADMIN_CATEGORY_ASSETS.get("css", None),
            js=settings.LOTUS_ADMIN_CATEGORY_ASSETS.get("js", None)
        )

    def get_language(self):
        language = (
            self.kwargs.get(self.language_kwarg) or
            self.request.GET.get(self.language_kwarg) or
            None
        )

        if language and language not in dict(settings.LANGUAGES):
            raise Http404(
                _("Language '{}' is unknown from 'settings.LANGUAGES'").format(language)
            )

        return language

    def get_context_data(self, **kwargs):
        """
        Append specific admin context.

        This includes:

        * The page title;
        * The tree object;
        * The media object;
        """
        context = super().get_context_data(**kwargs)

        current_language = self.get_language()

        if current_language:
            title = _("Category tree for language '%(lang)s'") % {
                "lang": current_language
            }
        else:
            title = _("Category tree")

        tree = Category.get_nested_tree(language=current_language)

        context.update({
            "title": title,
            "tree": tree,
            "view_base_medias": self.get_view_media(),
        })

        return context
