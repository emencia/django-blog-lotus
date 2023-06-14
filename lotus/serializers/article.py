from rest_framework import serializers

from taggit.serializers import TagListSerializerField, TaggitSerializer

from ..models import Article
from .author import AuthorSerializer
from .category import CategorySerializer


class ArticleSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    detail_url = serializers.SerializerMethodField()
    original = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='lotus:api-article-detail'
    )
    tags = TagListSerializerField()
    authors = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
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

    def get_authors(self, obj):
        return AuthorSerializer(obj.authors, many=True, context=self.context).data

    def get_categories(self, obj):
        return CategorySerializer(obj.categories, many=True, context=self.context).data

    def get_related(self, obj):
        return []
