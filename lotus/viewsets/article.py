from rest_framework import viewsets

from ..models import Article
from ..serializers import ArticleSerializer, ArticleResumeSerializer

from .mixins import ArticleFilterAbstractViewset, MultiSerializerViewSetMixin


class ArticleViewSet(MultiSerializerViewSetMixin, ArticleFilterAbstractViewset,
                     viewsets.ReadOnlyModelViewSet):
    """
    Entrypoint for Article listing and detail.
    """
    model = Article
    serializer_class = ArticleResumeSerializer
    serializer_action_classes = {
        "retrieve": ArticleSerializer,
    }

    def get_queryset(self):
        """
        Get the base queryset which may include the basic publication filter
        depending preview mode.

        Also apply lookup for "private" mode for non authenticated users.

        .. Note::
            Opposed to HTML views, this does not support (yet) the preview mode.
        """
        q = self.apply_article_lookups(self.model.objects, self.get_language_code())

        return q.order_by(*self.model.COMMON_ORDER_BY)
