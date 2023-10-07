from ..views.mixins import ArticleFilterMixin, LanguageMixin


class ArticleFilterAbstractViewset(ArticleFilterMixin, LanguageMixin):
    """
    A viewset abstract to gather mixins for including methods to apply publication
    criteria and language filter.
    """

    def get_serializer_context(self):
        """
        Provide useful Lotus context to serializers used in viewset.
        """
        context = super().get_serializer_context()
        context["LANGUAGE_CODE"] = self.get_language_code()
        context["article_filter_func"] = getattr(self, "apply_article_lookups")
        context["lotus_now"] = getattr(self, "target_date")
        return context


class MultiSerializerViewSetMixin:
    """
    A mixin to allow for selectable serializer per action in a viewset.

    Attributes:
        serializer_action_classes (dict): Registry of defined serializer for each
            available viewset action. Concretely an item key is the action name and
            item value is a serializer class.

            Action names are exactly the same
            than the ones implemented in DRF viewsets or custom ones implemented by
            your own viewset.

            The basic viewset attribute ``serializer_class`` is still required to be
            defined because it is the default one used when there is no custom rule for
            current action OR in some cases where the viewset won't have attribute
            ``action``.

            Example: ::

                serializer_class = MyDefaultSerializer
                serializer_action_classes = {
                    "list": MyListSerializer,
                    "my_action": MyActionSerializer,
                }

    Inspired from:
    https://stackoverflow.com/questions/22616973/django-rest-framework-use-different-serializers-in-the-same-modelviewset
    """
    serializer_action_classes = {}

    def get_serializer_class(self):
        """
        Look for a custom serializer class in attribute
        ``MultiSerializerViewSetMixin.serializer_action_classes``.
        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
