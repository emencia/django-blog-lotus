from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from ...models import Article
from ...forms import TranslateToLangForm
from .mixins import CustomLotusAdminContext


class ArticleAdminTranslateView(CustomLotusAdminContext, DetailView):
    """
    Display a form to select a language to translate an article to.

    The form does not perform a POST request. Instead it will make a GET to the article
    create form with some URL argument so the create form will know it will have to
    prefill fields "language" and "original", the user still have to fill everything
    else.

    Form only displays the language which are still available (not in original and
    its possible translations).

    Given ID is used to retrieve an Article object and get its original if its
    translation. Finally the form will always redirect to an original article.

    There is some validation around targeted object to ensure a
    """
    model = Article
    template_name = "admin/lotus/article/translate_original.html"
    context_object_name = "requested_article"
    pk_url_kwarg = "id"

    def get_queryset(self):
        return Article.objects.all()

    def get_object(self, queryset=None):
        requested_object = super().get_object(queryset=queryset)

        # The requested object is already an original
        if requested_object.original is None:
            self.original = requested_object
        else:
            self.original = requested_object.original

        return requested_object

    def get_context_data(self, **kwargs):
        """
        Append required admin context
        """
        # All article translation around origin including itself
        existing = self.model.objects.get_siblings(
            source=self.original
        )
        existing = [self.original] + list(existing)

        # All language from existing article translations
        article_languages = [item.language for item in existing]

        # All available language names and codes, suitable to a choice field
        available_languages = [
            item
            for item in settings.LANGUAGES
            if (item[0] not in article_languages)
        ]

        # Only enable form if there is at least one available language
        translate_form = None
        if available_languages:
            translate_form = TranslateToLangForm(
                available_languages=available_languages
            )

        context = super().get_context_data(**kwargs)
        context.update({
            "title": _("Translate '%(title)s'") % {'title': self.object.title},
            "original_article": self.original,
            "is_original": (self.object == self.original),
            "existing_articles": existing,
            "article_languages": article_languages,
            "available_language": available_languages,
            "form": translate_form,
        })

        return context
