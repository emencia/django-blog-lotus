from rest_framework import serializers

from taggit.serializers import TagListSerializerField, TaggitSerializer

from ..models import Article
from .author import AuthorResumeSerializer
from .category import CategoryResumeSerializer


class ArticleSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    """
    This is the serializer for full payload (opposed to the resumed one) which should
    be reserved for detail only.

    TODO:

    * May include media formats;
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
        return obj.publish_datetime()

    def get_authors(self, obj):
        return AuthorResumeSerializer(obj.authors, many=True, context=self.context).data

    def get_categories(self, obj):
        return CategoryResumeSerializer(obj.categories, many=True, context=self.context).data

    def get_related(self, obj):
        return ArticleResumeSerializer(obj.get_related(), many=True, context=self.context).data


class ArticleResumeSerializer(ArticleSerializer):
    """
    Enlighted article serializer

    This should be the common serializer, the other complete one would be better in
    detail.

    TODO: White list of fields to implement

    * url
    * detail_url
    * title
    * slug
    * cover
    * status resume
    * publish date (condensed date and time? could be done at ArticleSerializer level)
    * introduction
    * authors (with resumed serializer)
    * categories (with resumed serializer)
    * related (with resumed serializer)
    * tags (with resumed serializer)
    * seo_title

    """

    class Meta:
        model = Article
        fields = [
            "url",
            "detail_url",
            "language",
            "slug",
            "publish_datetime",
            "title",
            "seo_title",
            "cover",
            "introduction",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus:api-article-detail"
            },
        }