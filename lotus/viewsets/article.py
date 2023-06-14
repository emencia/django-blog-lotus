from rest_framework import viewsets

from ..models import Article
from ..serializers import ArticleSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):

    model = Article
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return self.model.objects.all()
