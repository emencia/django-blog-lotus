from django.conf import settings

from ..models import Article

from .translated import TranslatedSitemapAbstract


class ArticleSitemap(TranslatedSitemapAbstract):
    """
    Article sitemap list only original objects or all objects depending ``translations``
    attribute.

    When translation mode is enabled, each original object will list its translations
    as alternative links.

    Opposed to ``django.contrib.sitemaps.Sitemap`` class, this does not support
    ``i18n``, ``alternates`` and ``x_default`` attributes.

    This sitemap class supports also some additionnal options ``pinned_priority``and
    ``featured_priority`` that allow to define a specific priority depending the article
    is pinned, featured or not.
    """
    changefreq = settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("changefreq")
    limit = settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("limit", 50000)
    protocol = settings.LOTUS_SITEMAP_CATEGORY_OPTIONS.get("protocol")
    translations = settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("translations", True)
    model = Article

    def items(self):
        """
        Return model items to reference.

        This will only list original objects that can be seen without any permission,
        so no private or non published contents. Each original may have alternate links
        for their translations.
        """
        q = self.model.objects.get_published(private=False)

        if self.translations:
            return q.filter(original__isnull=True)

        return q

    def lastmod(self, obj):
        return obj.last_update

    def priority(self, obj):
        if (
            settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("featured_priority") and
            obj.featured is True
        ):
            return settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("featured_priority")

        if (
            settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("pinned_priority") and
            obj.pinned is True
        ):
            return settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("pinned_priority")

        return settings.LOTUS_SITEMAP_ARTICLE_OPTIONS.get("priority")
