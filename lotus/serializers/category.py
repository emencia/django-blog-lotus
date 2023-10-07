from rest_framework import serializers

from ..models import Category


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """
    Other used model serializer are imported into methods to avoid circular references.
    """
    original = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="lotus-api:category-detail"
    )
    detail_url = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:category-detail"
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
                obj.articles, obj.language
            )
        else:
            queryset = obj.articles.filter(language=obj.language)

        return ArticleMinimalSerializer(
            queryset,
            many=True,
            context=self.context
        ).data


class CategoryResumeSerializer(CategorySerializer):
    """
    Reduced category serializer

    This should be the common serializer, the other complete one would be better in
    detail.
    """
    class Meta:
        model = Category
        fields = [
            "url",
            "detail_url",
            "language",
            "title",
            "lead",
            "cover",
            "description",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:category-detail"
            },
        }


class CategoryMinimalSerializer(CategorySerializer):
    """
    Minimal category serializer

    Only contain the minimal category informations, mostly used to list category items.
    """
    class Meta:
        model = Category
        fields = [
            "url",
            "detail_url",
            "language",
            "title",
            "lead",
            "cover",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:category-detail"
            },
        }
