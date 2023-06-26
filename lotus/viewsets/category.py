from rest_framework import viewsets

from ..models import Category
from ..serializers import CategorySerializer, CategoryResumeSerializer

from .mixins import MultiSerializerViewSetMixin


class CategoryViewSet(MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    TODO: Must implement lookup criterions
    """

    model = Category
    serializer_class = CategoryResumeSerializer
    serializer_action_classes = {
        "retrieve": CategorySerializer,
    }

    def get_queryset(self):
        return self.model.objects.all()
