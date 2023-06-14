from rest_framework import viewsets

from ..models import Category
from ..serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):

    model = Category
    serializer_class = CategorySerializer

    def get_queryset(self):
        return self.model.objects.all()
