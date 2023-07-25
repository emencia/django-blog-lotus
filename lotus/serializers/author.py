from rest_framework import serializers

from ..models import Author


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    """
    Author serializer only share a few fields since we don't want to expose security
    concern informations about users.

    TODO: Missing related article list for details only ?
    """
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            "url",
            "detail_url",
            "username",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus:api-author-detail"
            },
        }

    def get_detail_url(self, obj):
        """
        Return the HTML detail view URL.
        """
        return obj.get_absolute_url()


class AuthorResumeSerializer(AuthorSerializer):

    class Meta:
        model = Author
        fields = [
            "url",
            "detail_url",
            "username",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "url": {
                "view_name": "lotus:api-author-detail"
            },
        }
