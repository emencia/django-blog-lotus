from django.conf import settings

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
        """
        q = self.model.objects.all()

        if (
            not settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE or
            self.action != "retrieve"
        ):
            q = self.apply_article_lookups(q, self.get_language_code())
        else:
            q = self.apply_article_lookups(q)

        return q.order_by(*self.model.COMMON_ORDER_BY)
