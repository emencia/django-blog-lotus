from django import forms


class TranslatedModelChoiceField(forms.ModelChoiceField):
    """
    Customize ModelChoiceField for model which inherit from ``Translated``
    model to display object language in brackets.
    """
    def label_from_instance(self, obj):
        return "{title} [{lang}]".format(
            title=str(obj),
            lang=obj.get_language_display(),
        )


class TranslatedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Customize ModelMultipleChoiceField for model which inherit from ``Translated``
    model to display object language in brackets.
    """
    def label_from_instance(self, obj):
        return "{title} [{lang}]".format(
            title=str(obj),
            lang=obj.get_language_display(),
        )
