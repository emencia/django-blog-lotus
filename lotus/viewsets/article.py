from rest_framework import viewsets

from ..models import Article
from ..serializers import ArticleSerializer, ArticleResumeSerializer

from .mixins import ArticleFilterAbstractViewset, MultiSerializerViewSetMixin


class ArticleViewSet(MultiSerializerViewSetMixin, ArticleFilterAbstractViewset,
                     viewsets.ReadOnlyModelViewSet):
    """
    TODO: Implemented lookup criteria, now test it
    """

    model = Article
    serializer_class = ArticleResumeSerializer
    serializer_action_classes = {
        "retrieve": ArticleSerializer,
    }

    #def get_queryset(self):
        #return self.model.objects.all()

    def get_queryset(self):
        """
        Get the base queryset which may include the basic publication filter
        depending preview mode.

        Preview mode is enabled from a flag in session and only for staff user. If it is
        disabled publication criterias are applied on lookups.

        Also apply lookup for "private" mode for non authenticated users.
        """
        q = self.apply_article_lookups(self.model.objects, self.get_language_code())

        return q.order_by(*self.model.COMMON_ORDER_BY)
