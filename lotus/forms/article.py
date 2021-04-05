from django import forms
from django.conf import settings

from ..models import Article


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
    """
    class Meta:
        model = Article
        widgets = {
            "introduction": CKEditorWidget(config_name=CONFIG_NAME),
            "content": CKEditorWidget(config_name=CONFIG_NAME),
        }
        exclude = [
            "last_update",
        ]
