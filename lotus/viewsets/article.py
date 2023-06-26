from rest_framework import viewsets

from ..models import Article
from ..serializers import ArticleSerializer, ArticleResumeSerializer

from .mixins import MultiSerializerViewSetMixin


class ArticleViewSet(MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    TODO: Must implement lookup criterions
    """

    model = Article
    serializer_class = ArticleResumeSerializer
    serializer_action_classes = {
        "retrieve": ArticleSerializer,
    }

    def get_queryset(self):
        return self.model.objects.all()
