from rest_framework import viewsets

from ..models import Author
from ..serializers import AuthorSerializer, AuthorResumeSerializer

from .mixins import MultiSerializerViewSetMixin


class AuthorViewSet(MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Author
    serializer_class = AuthorResumeSerializer
    serializer_action_classes = {
        "retrieve": AuthorSerializer,
    }

    def get_queryset(self):
        return self.model.objects.all()
