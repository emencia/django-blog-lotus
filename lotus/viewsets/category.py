from django.conf import settings

from rest_framework import viewsets

from ..models import Category
from ..serializers import CategorySerializer, CategoryResumeSerializer

from .mixins import ArticleFilterAbstractViewset, MultiSerializerViewSetMixin


class CategoryViewSet(MultiSerializerViewSetMixin, ArticleFilterAbstractViewset,
                      viewsets.ReadOnlyModelViewSet):
    """
    Entrypoint for Category listing and detail.
    """

    model = Category
    serializer_class = CategoryResumeSerializer
    serializer_action_classes = {
        "retrieve": CategorySerializer,
    }

    def get_queryset(self):
        """
        Build queryset base with language filtering to list categories.
        """
        q = self.model.objects.all()

        if (
            not settings.LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE or
            self.action != "retrieve"
        ):
            q = q.get_for_lang(self.get_language_code())

        return q.order_by(*self.model.COMMON_ORDER_BY)
