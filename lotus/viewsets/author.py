from rest_framework import viewsets

from ..models import Author
from ..serializers import AuthorSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    model = Author
    serializer_class = AuthorSerializer

    def get_queryset(self):
        return self.model.objects.all()
