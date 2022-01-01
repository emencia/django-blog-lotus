from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from ...forms import TranslateToLangForm


class CustomLotusAdminContext:
    """
    Mixin to add required context for a custom model admin view.

    The view which use it must have the ``model`` correctly set to your model, if your
    view has no model then this mixin is probably useless.

    Also, there is an additional useful context variable ``title`` to set yourself in
    your view since its value is totally related to the view itself.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
            "app_label": self.model._meta.app_label,
            "app_path": self.request.get_full_path(),

        })

        return context


class AdminTranslateView(CustomLotusAdminContext, DetailView):
    """
    Mixin to display a form to select a language to translate an object to.

    The form does not perform a POST request. Instead it will make a GET to the object
    create form with some URL argument so the create form will know it will have to
    prefill fields "language" and "original", the user still have to fill everything
    else.

    Form only displays the language which are still available (not in original and
    its possible translations).

    Given ID is used to retrieve an object and get its original if its
    translation. Finally the form will always redirect to an original object.

    Despite inheriting from DetailView, this is not a ready to use view, you need
    inherit it to define the ``mode`` and ``template_name`` attributes correctly.
    """
    model = None
    template_name = None
    context_object_name = "requested_object"
    pk_url_kwarg = "id"

    def get_queryset(self):
        return self.model.objects.all()

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
        Append specific admin context
        """
        # All object translation around origin including itself
        existing = self.model.objects.get_siblings(
            source=self.original
        )
        existing = [self.original] + list(existing)

        # All language from existing object translations
        object_languages = [item.language for item in existing]

        # All available language names and codes, suitable to a choice field
        available_languages = [
            item
            for item in settings.LANGUAGES
            if (item[0] not in object_languages)
        ]

        # Only enable form if there is at least one available language
        translate_form = None
        if available_languages:
            translate_form = TranslateToLangForm(
                available_languages=available_languages
            )

        context = super().get_context_data(**kwargs)
        context.update({
            "title": _("Translate '%(title)s'") % {"title": self.object.title},
            "original_object": self.original,
            "is_original": (self.object == self.original),
            "existing_objects": existing,
            "object_languages": object_languages,
            "available_language": available_languages,
            "form": translate_form,
        })

        return context
