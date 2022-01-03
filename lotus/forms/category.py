from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..models import Category

from .translated import TranslatedModelChoiceField


# Use the right field depending 'ckeditor_uploader' app is enabled or not
if "ckeditor_uploader" in settings.INSTALLED_APPS:
    from ckeditor_uploader.widgets import CKEditorUploadingWidget as CKEditorWidget
else:
    from ckeditor.widgets import CKEditorWidget


# Use the specific CKEditor config if any
CONFIG_NAME = "lotus"
CKEDITOR_CONFIG = getattr(settings, "CKEDITOR_CONFIGS", {})
if CONFIG_NAME not in CKEDITOR_CONFIG:
    CONFIG_NAME = "default"


class CategoryAdminForm(forms.ModelForm):
    """
    Category form for admin.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Model choices querysets for create form get all objects since there is no
        # data yet to constraint
        if not self.instance.pk:
            original_queryset = Category.objects.filter(original__isnull=True)
        # Model choices querysets for change form filter objects against constraints
        else:
            # Avoid selecting itself, a translation or object with the same language
            original_queryset = Category.objects.filter(original__isnull=True).exclude(
                models.Q(id=self.instance.id) |
                models.Q(language=self.instance.language)
            )

        # Apply choice limit on 'original' field queryset to avoid selecting
        # itself or object with the same language
        # NOTE: This trick drop the help_text from model
        self.fields["original"] = TranslatedModelChoiceField(
            queryset=original_queryset,
            required=False,
            blank=True,
        )

    def clean(self):
        """
        Add custom global input cleaner validations.
        """
        cleaned_data = super().clean()
        original = cleaned_data.get("original")
        language = cleaned_data.get("language")

        if original and original.language == language:
            self.add_error(
                "language",
                forms.ValidationError(
                    _(
                        "You can't have a language identical to the original "
                        "relation."
                    ),
                    code="invalid",
                ),
            )
            self.add_error(
                "original",
                forms.ValidationError(
                    _(
                        "You can't have an original relation in the same language."
                    ),
                    code="invalid",
                ),
            )

        if (
            self.instance.pk and
            self.instance.articles.exclude(language=language).count() > 0
        ):
            self.add_error(
                "language",
                forms.ValidationError(
                    _(
                        "Some article in different language relate to this "
                        "category, you can't change language until those article "
                        "are not related anymore."
                    ),
                    code="invalid-language",
                ),
            )

    class Meta:
        model = Category
        widgets = {
            "description": CKEditorWidget(config_name=CONFIG_NAME),
        }
        fields = "__all__"
