from rest_framework import viewsets

from ..models import Author
from ..serializers import AuthorSerializer, AuthorResumeSerializer

from .mixins import ArticleFilterAbstractViewset, MultiSerializerViewSetMixin


class AuthorViewSet(MultiSerializerViewSetMixin, ArticleFilterAbstractViewset,
                    viewsets.ReadOnlyModelViewSet):
    """
    Entrypoint for Author listing and detail.
    """

    model = Author
    serializer_class = AuthorResumeSerializer
    serializer_action_classes = {
        "retrieve": AuthorSerializer,
    }

    def get_queryset(self):
        q = self.model.lotus_objects.get_active(language=self.get_language_code())

        return q.order_by(*self.model.COMMON_ORDER_BY)
