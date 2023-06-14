from rest_framework import viewsets

from ..models import Author
from ..serializers import AuthorSerializer, AuthorResumeSerializer

from .mixins import ArticleFilterAbstractViewset, MultiSerializerViewSetMixin


class AuthorViewSet(MultiSerializerViewSetMixin, ArticleFilterAbstractViewset,
                    viewsets.ReadOnlyModelViewSet):
    """
    Entrypoint to list authors which are related at least to one article.
    """

    model = Author
    serializer_class = AuthorResumeSerializer
    serializer_action_classes = {
        "retrieve": AuthorSerializer,
    }

    def get_queryset(self):
        q = self.model.lotus_objects.get_active(
            language=self.get_language_code(),
            private=None if self.request.user.is_authenticated else False,
        )

        return q.order_by(*self.model.COMMON_ORDER_BY)
