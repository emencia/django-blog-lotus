from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.db import models
from django.urls import translate_url, reverse

from taggit.models import Tag

from ..views.mixins import ArticleFilterMixin


class TagSitemap(ArticleFilterMixin, Sitemap):
    """
    Tag sitemap only list tags that have at least an article.
    """
    changefreq = settings.LOTUS_SITEMAP_TAG_OPTIONS.get("changefreq")
    limit = settings.LOTUS_SITEMAP_TAG_OPTIONS.get("limit", 50000)
    priority = settings.LOTUS_SITEMAP_TAG_OPTIONS.get("priority")
    protocol = settings.LOTUS_SITEMAP_TAG_OPTIONS.get("protocol")
    model = Tag

    def location(self, item):
        """
        Return localized url for the tag language (defined through annotation from
        queryset).
        """
        return translate_url(
            reverse("lotus:tag-detail", kwargs={"tag": item.slug}),
            item.article_language
        )

    def lastmod(self, obj):
        """
        Assume latest tag update from the last related article update that was annoted
        in queryset.

        Returns:
            datetime: The latest datetime found from active articles related to tag.
        """
        return obj.article_latest_update

    def items(self):
        """
        Get all active Tag object to reference.

        We need to retrieve object separatly for each available language because
        we filter for active tag per language. So we try to do it more efficiently with
        ``union()``.

        Returns:
            Queryset: Combined lookups in a single queryset.
        """
        return self.model.objects.none().union(*[
            self.get_language_items(code)
            for code, name in settings.LANGUAGES
        ]).order_by("article_language", "name")

    def get_language_items(self, language):
        """
        Return active Tags for a language.

        Published articles are determined with the common publication criterias.

        Arguments:
            language (string): Language code to filter on. It will also annotate
                objects so their language can be retrieved for further usage.

        Returns:
            Queryset: Build complex queryset to get all tags which have published
            articles for required language.
        """
        publication_criterias = self.build_article_lookups(
            language=language,
            prefix="article__",
        )

        return self.model.objects.annotate(
            article_language=models.Value(language),
            article_latest_update=models.Max("article__last_update"),
            article_count=models.Count(
                "article",
                filter=models.Q(*publication_criterias),
            )
        ).filter(article_count__gt=0)
