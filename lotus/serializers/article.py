from rest_framework import serializers

from taggit.serializers import TagListSerializerField, TaggitSerializer

from ..models import Article
from .author import AuthorResumeSerializer
from .category import CategoryResumeSerializer
from ..templatetags.lotus import article_state_list


class ArticleSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    """
    This is the serializer for full payload which implement every possible fields.
    """
    detail_url = serializers.SerializerMethodField()
    original = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='lotus:api-article-detail'
    )
    tags = TagListSerializerField()
    authors = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    publish_datetime = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    states = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = "__all__"
        extra_kwargs = {
            "url": {
                "view_name": "lotus:api-article-detail"
            },
        }

    def get_detail_url(self, obj):
        """
        Return the HTML detail view URL.
        """
        return obj.get_absolute_url()

    def get_publish_datetime(self, obj):
        return obj.publish_datetime().isoformat()

    def get_authors(self, obj):
        return AuthorResumeSerializer(
            obj.authors,
            many=True,
            context=self.context
        ).data

    def get_categories(self, obj):
        return CategoryResumeSerializer(
            obj.categories,
            many=True,
            context=self.context
        ).data

    def get_related(self, obj):
        return ArticleMinimalSerializer(
            obj.get_related(),
            many=True,
            context=self.context
        ).data

    def get_states(self, obj):
        return article_state_list({}, obj, now=self.context.get("lotus_now", None))


class ArticleResumeSerializer(ArticleSerializer):
    """
    Enlighted article serializer

    This should be the common serializer, the other complete one would be better in
    detail.

    .. Note::

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
                "view_name": "lotus:api-article-detail"
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
                "view_name": "lotus:api-article-detail"
            },
        }
