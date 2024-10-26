from rest_framework import serializers

from taggit.serializers import TagListSerializerField, TaggitSerializer

from ..models import Article
from ..templatetags.lotus import article_state_list


class ArticleSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    """
    This is the serializer for full payload which implement every possible fields.

    Other used model serializer are imported into methods to avoid circular references.
    """
    detail_url = serializers.SerializerMethodField()
    original = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="lotus-api:article-detail"
    )
    tags = TagListSerializerField()
    authors = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    publish_datetime = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    states = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    translations = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = "__all__"
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:article-detail"
            },
        }

    def get_detail_url(self, obj):
        """
        Return the HTML detail view URL.

        TODO: Add a new settings to disallow for detail_url and return just None (so
        payload format is still the same with just empty value).
        """
        return obj.get_absolute_url()

    def get_publish_datetime(self, obj):
        """
        Return the consolidated published datetime in ISO format.
        """
        return obj.publish_datetime().isoformat()

    def get_authors(self, obj):
        """
        Return list of related authors.
        """
        from .author import AuthorResumeSerializer

        return AuthorResumeSerializer(
            obj.get_authors(),
            many=True,
            context=self.context
        ).data

    def get_categories(self, obj):
        """
        Return list of related categories.

        Categories with different language than the article one are filtered out.
        """
        from .category import CategoryMinimalSerializer

        return CategoryMinimalSerializer(
            obj.get_categories(),
            many=True,
            context=self.context
        ).data

    def get_related(self, obj):
        """
        Return list of related articles.
        """
        if self.context.get("article_filter_func"):
            queryset = obj.get_related(
                filter_func=self.context.get("article_filter_func")
            )
        else:
            queryset = obj.get_related()

        return ArticleMinimalSerializer(
            queryset,
            many=True,
            context=self.context
        ).data

    def get_states(self, obj):
        """
        Return a list of article state computed from some of its field according to
        ``article_state_list()`` behavior.
        """
        return article_state_list({}, obj, now=self.context.get("lotus_now", None))

    def get_album(self, obj):
        """
        Return album data with its items.
        """
        from .album import AlbumSerializer

        if not obj.album:
            return None

        return AlbumSerializer(
            obj.album,
            many=False,
            context=self.context
        ).data

    def get_translations(self, obj):
        """
        Return list of possible translations.
        """
        queryset = self.Meta.model.objects.filter(original=obj.id)

        if self.context.get("article_filter_func"):
            queryset = self.context.get("article_filter_func")(queryset)

        return ArticleMinimalSerializer(
            queryset.order_by(*self.Meta.model.COMMON_ORDER_BY),
            many=True,
            context=self.context
        ).data


class ArticleResumeSerializer(ArticleSerializer):
    """
    Reduced article serializer

    This should be the common serializer, the other complete one would be better for
    details.

    .. Note::

        Some fields
        Field ``related`` is not allowed since this serializer is used into list and
        it could lead on too many recursions.

    """

    class Meta:
        model = Article
        fields = [
            "authors",
            "categories",
            "cover",
            "detail_url",
            "introduction",
            "language",
            "publish_datetime",
            "seo_title",
            "slug",
            "states",
            "tags",
            "title",
            "url",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:article-detail"
            },
        }


class ArticleMinimalSerializer(ArticleSerializer):
    """
    Minimal article serializer

    Only contain the minimal article informations, mostly used to list article items
    with possible recursions like on 'Article.related'.
    """

    class Meta:
        model = Article
        fields = [
            "cover",
            "detail_url",
            "introduction",
            "language",
            "publish_datetime",
            "states",
            "title",
            "url",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus-api:article-detail"
            },
        }
