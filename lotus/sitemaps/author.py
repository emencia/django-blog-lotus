from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.db import models
from django.urls import translate_url

from ..models import Author


class AuthorSitemap(Sitemap):
    """
    Author sitemap only list authors that have at least an article.
    """
    changefreq = settings.LOTUS_SITEMAP_AUTHOR_OPTIONS.get("changefreq")
    limit = settings.LOTUS_SITEMAP_AUTHOR_OPTIONS.get("limit", 50000)
    priority = settings.LOTUS_SITEMAP_AUTHOR_OPTIONS.get("priority")
    protocol = settings.LOTUS_SITEMAP_AUTHOR_OPTIONS.get("protocol")
    model = Author

    def location(self, item):
        """
        Return localized url for the author language (defined through annotation from
        queryset).
        """
        return translate_url(
            item.get_absolute_url(),
            item.article_language
        )

    def lastmod(self, obj):
        """
        Assume latest author update from the last related article update that was
        annoted in queryset.

        Returns:
            datetime: The latest datetime found from active articles related to author.
        """
        return obj.article_latest_update

    def items(self):
        """
        Get all active Author object to reference.

        We need to retrieve object separatly for each available language because
        we filter for active tag per language. So we try to do it more efficiently with
        ``union()``.

        Returns:
            Queryset: Combined lookups in a single queryset.
        """
        return self.model.objects.none().union(*[
            self.get_language_items(code)
            for code, name in settings.LANGUAGES
        ]).order_by("article_language", *self.model.COMMON_ORDER_BY)

    def get_language_items(self, language):
        """
        Return active Author for a language.

        Published articles are determined with the common publication criterias.

        Arguments:
            language (string): Language code to filter on. It will also annotate
                objects so their language can be retrieved for further usage.

        Returns:
            Queryset: Build complex queryset to get all tags which have published
            articles for required language.
        """
        return self.model.lotus_objects.get_active(
            language=language,
            private=False,
        ).annotate(
            article_language=models.Value(language),
            article_latest_update=models.Max("articles__last_update"),
        )
