from django import forms
from django.utils.translation import gettext_lazy as _


class TranslateToLangForm(forms.Form):
    """
    A very basic non model form just for listing available language choices.
    """
    language = forms.ChoiceField(
        label=_("Available languages"),
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        available_languages = kwargs.pop("available_languages", [])
        super().__init__(*args, **kwargs)

        self.fields["language"].choices = available_languages
