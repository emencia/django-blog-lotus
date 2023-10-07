from rest_framework import serializers

from ..models import Author


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    """
    Author serializer only share a few fields since we don't want to expose security
    concern informations about users.
    """
    detail_url = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            "url",
            "detail_url",
            "username",
            "first_name",
            "last_name",
            "articles",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:author-detail"
            },
        }

    def get_detail_url(self, obj):
        """
        Return the HTML detail view URL.
        """
        return obj.get_absolute_url()

    def get_articles(self, obj):
        """
        Return list of articles related to category object.

        On default, only language filtering is applied on queryset but if serialized is
        provided a context with item ``article_filter_func`` it will assume it is a
        filtering function expecting the same arguments as
        ``ArticleFilterMixin.apply_article_lookups`` and also some viewset attributes
        like ``request``.
        """
        from .article import ArticleMinimalSerializer

        if self.context.get("article_filter_func"):
            queryset = self.context.get("article_filter_func")(
                obj.articles, self.context.get("LANGUAGE_CODE")
            )
        else:
            queryset = obj.articles.filter(language=self.context.get("LANGUAGE_CODE"))

        return ArticleMinimalSerializer(
            queryset,
            many=True,
            context=self.context
        ).data


class AuthorResumeSerializer(AuthorSerializer):

    class Meta:
        model = Author
        fields = [
            "url",
            "detail_url",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:author-detail"
            },
        }
