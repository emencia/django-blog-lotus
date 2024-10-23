from django.conf import settings

from ..models import Category

from .translated import TranslatedSitemapAbstract


class CategorySitemap(TranslatedSitemapAbstract):
    """
    Category sitemap list only original objects or all objects depending
    ``translations`` attribute.

    When translation mode is enabled, each original object will list its translations
    as alternative links.

    Opposed to ``django.contrib.sitemaps.Sitemap`` class, this does not support
    ``i18n``, ``alternates`` and ``x_default`` attributes.
    """
    changefreq = settings.LOTUS_SITEMAP_CATEGORY_OPTIONS.get("changefreq")
    limit = settings.LOTUS_SITEMAP_CATEGORY_OPTIONS.get("limit", 50000)
    priority = settings.LOTUS_SITEMAP_CATEGORY_OPTIONS.get("priority")
    protocol = settings.LOTUS_SITEMAP_CATEGORY_OPTIONS.get("protocol")
    translations = settings.LOTUS_SITEMAP_CATEGORY_OPTIONS.get("translations", True)
    model = Category

    def items(self):
        """
        Return model items to reference.
        """
        q = self.model.objects.all().order_by(*Category.COMMON_ORDER_BY)

        if self.translations:
            return q.filter(original__isnull=True)

        return q

    def lastmod(self, obj):
        return obj.modified
