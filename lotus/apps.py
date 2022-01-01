from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LotusConfig(AppConfig):
    name = "lotus"
    verbose_name = _("Lotus weblog")
    default_auto_field = "django.db.models.AutoField"
