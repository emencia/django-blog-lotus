from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..models import Article, Category


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


class ArticleAdminForm(forms.ModelForm):
    """
    Article form for admin.

    TODO:
        Insert language code on each select option alike "My category [fr-fr]".
        May need to use a custom widget for original, categories, related.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply choice limit on fields querysets
        if self.instance.pk:
            # Avoid selecting itself or object with the same language
            self.fields["original"].queryset = Article.objects.exclude(
                models.Q(id=self.instance.pk) |
                models.Q(language=self.instance.language)
            )
            # Avoid selecting itself or object with a different language
            self.fields["related"].queryset = Article.objects.filter(
                language=self.instance.language
            ).exclude(
                id=self.instance.pk
            )
            # Avoid selecting object with a different language
            self.fields["categories"].queryset = Category.objects.filter(
                language=self.instance.language
            )

    def clean(self):
        """
        Add custom global input cleaner validations.
        """
        cleaned_data = super().clean()
        original = cleaned_data.get("original")
        language = cleaned_data.get("language")
        related = cleaned_data.get("related")
        categories = cleaned_data.get("categories")

        # Ensure original lang and current article language are identical
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

        # Ensure related articles languages are the same than the current article
        # language, this is only for create form since there is choice validation
        # in change form which is enough.
        if (
            not self.instance.pk and
            related and
            related.exclude(language=language).count() > 0
        ):
            self.add_error(
                "related",
                forms.ValidationError(
                    _(
                        "You can't have related articles in different language."
                    ),
                    code="invalid-related",
                ),
            )

        # Ensure categories languages are the same than the current article
        # language, this is only for create form since there is choice validation
        # in change form which is enough.
        if (
            not self.instance.pk and
            categories and
            categories.exclude(language=language).count() > 0
        ):
            self.add_error(
                "categories",
                forms.ValidationError(
                    _(
                        "You can't have categories in different language."
                    ),
                    code="invalid-categories",
                ),
            )

    class Meta:
        model = Article
        widgets = {
            "introduction": CKEditorWidget(config_name=CONFIG_NAME),
            "content": CKEditorWidget(config_name=CONFIG_NAME),
        }
        exclude = [
            "last_update",
        ]
