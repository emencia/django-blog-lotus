from rest_framework import serializers

from ..models import Category


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """
    TODO: Missing related article list, however this is not something we want to have
    in all payload, only for the details.
    """

    original = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="lotus-api:category-detail"
    )
    detail_url = serializers.SerializerMethodField()

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
