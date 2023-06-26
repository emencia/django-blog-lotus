from rest_framework import serializers

from ..models import Category


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """
    TODO: Missing related article list
    """

    original = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='lotus:api-category-detail'
    )
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {
            "url": {
                "view_name": "lotus:api-category-detail"
            },
        }

    def get_detail_url(self, obj):
        """
        Return the HTML detail view URL.
        """
        return obj.get_absolute_url()


class CategoryResumeSerializer(CategorySerializer):

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
                "view_name": "lotus:api-category-detail"
            },
        }

