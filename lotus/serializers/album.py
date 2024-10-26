from rest_framework import serializers

from ..models import Album, AlbumItem


class AlbumSerializer(serializers.ModelSerializer):
    """
    Album container serializer.

    It is only intended to be included in Article serializer because Album does not
    have dedicated endpoint.
    """
    items = serializers.SerializerMethodField()

    class Meta:
        model = Album
        exclude = ["id"]

    def get_items(self, obj):
        """
        Return list of album items.
        """
        return AlbumItemSerializer(
            obj.albumitems.all(),
            many=True,
            context=self.context
        ).data


class AlbumItemSerializer(serializers.ModelSerializer):
    """
    Album item serializer.
    """

    class Meta:
        model = AlbumItem
        exclude = ["album", "id"]
