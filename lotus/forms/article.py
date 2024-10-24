from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple

from dal import autocomplete

from ..models import Article, Category

from ..formfields import (
    TranslatedModelChoiceField, TranslatedModelMultipleChoiceField
)


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


class ArticleAdminForm(autocomplete.FutureModelForm):
    """
    Article form for admin.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Model choices querysets for create form get all objects since there is no
        # data yet to constraint
        if not self.instance.pk:
            original_queryset = Article.objects.filter(original__isnull=True)
            related_queryset = Article.objects.all()
            category_queryset = Category.objects.all()
        # Model choices querysets for change form filters objects against constraints
        else:
            # Avoid selecting itself, a translation or object with the same language
            original_queryset = Article.objects.filter(original__isnull=True).exclude(
                models.Q(id=self.instance.pk) |
                models.Q(language=self.instance.language)
            )
            # Avoid selecting itself or object with the same language
            related_queryset = Article.objects.filter(
                language=self.instance.language
            ).exclude(
                id=self.instance.pk
            )
            # Avoid selecting object with a different language
            category_queryset = Category.objects.filter(
                language=self.instance.language
            )

        # Enforce the right ordering for flat category list
        category_queryset = category_queryset.order_by(*Category.COMMON_ORDER_BY)

        # Use the right model choices fields for translated relations
        # NOTE: This trick drop the help_text from model
        self.fields["original"] = TranslatedModelChoiceField(
            queryset=original_queryset,
            required=False,
            blank=True,
        )
        self.fields["related"] = TranslatedModelMultipleChoiceField(
            queryset=related_queryset,
            widget=FilteredSelectMultiple("articles", is_stacked=False),
            required=False,
            blank=True,
        )
        self.fields["categories"] = TranslatedModelMultipleChoiceField(
            queryset=category_queryset,
            widget=FilteredSelectMultiple("categories", is_stacked=False),
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
        # language
        if (
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
        # language
        if (
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
        # For edition mode
        if self.instance.pk:
            # Check if an article has a translation, in this case it can not
            # select an original object since it is already an original.
            if original and Article.objects.filter(original_id=self.instance.pk):
                self.add_error(
                    "original",
                    forms.ValidationError(
                        _(
                            "This article already have a translation so it can not be "
                            "a translation itself."
                        ),
                        code="invalid-original",
                    ),
                )

    class Meta:
        model = Article
        widgets = {
            "introduction": CKEditorWidget(config_name=CONFIG_NAME),
            "content": CKEditorWidget(config_name=CONFIG_NAME),
            "tags": autocomplete.TaggitSelect2("lotus:tag-autocomplete"),
        }

        exclude = [
            "last_update",
        ]
