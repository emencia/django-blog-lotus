from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import Http404
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views import View

from taggit.models import Tag, TaggedItem

from ..models import Article
from .mixins import PreviewModeMixin, ArticleFilterMixin, LotusContextStage

try:
    from view_breadcrumbs import BaseBreadcrumbMixin
except ImportError:
    from .mixins import NoOperationBreadcrumMixin as BaseBreadcrumbMixin


class DisabledTagIndexView(View):
    """
    A very basic view which always return the common Http404 page.
    """
    def get(self, request, *args, **kwargs):
        raise Http404()


class EnabledTagIndexView(BaseBreadcrumbMixin, LotusContextStage, PreviewModeMixin,
                          ListView):
    """
    List of tags that are related from at least one article.
    """
    model = Tag
    template_name = "lotus/tag/list.html"
    paginate_by = settings.LOTUS_TAG_PAGINATION
    context_object_name = "tag_list"
    crumb_title = _("Tags")
    crumb_urlname = "lotus:tag-index"
    lotus_stage = "tags"

    @property
    def crumbs(self):
        return [
            (self.crumb_title, reverse(self.crumb_urlname)),
        ]

    def get_queryset(self):
        """
        TODO: The current queryset is naive about publication criterias
        """
        return Tag.objects.annotate(
            article_count=Count(
                "article",
                filter=Q(article__language=self.request.LANGUAGE_CODE)
            )
        ).filter(article_count__gt=0).order_by("name")


class TagDetailView(BaseBreadcrumbMixin, LotusContextStage, ArticleFilterMixin,
                    PreviewModeMixin, SingleObjectMixin, ListView):
    """
    Tag detail and its related article list.

    Opposed to article or category listing, this one list objects for language from
    request, not from the tag language since it dont have one.
    """
    model = Tag
    listed_model = Article
    template_name = "lotus/tag/detail.html"
    paginate_by = settings.LOTUS_ARTICLE_PAGINATION
    context_object_name = "tag_object"
    slug_field = "slug"
    slug_url_kwarg = "tag"
    pk_url_kwarg = None
    crumb_title = None  # No usage since title depends from object
    crumb_urlname = "lotus:tag-detail"
    lotus_stage = "tags"

    @property
    def crumbs(self):
        details_kwargs = {
            "tag": self.object.slug,
        }

        index_crumb_url = (
            reverse(EnabledTagIndexView.crumb_urlname)
            if settings.LOTUS_ENABLE_TAG_INDEX_VIEW
            else None
        )

        return [
            (EnabledTagIndexView.crumb_title, index_crumb_url),
            (str(self.object), reverse(self.crumb_urlname, kwargs=details_kwargs)),
        ]

    def get_queryset_for_object(self):
        """
        Build queryset base to get Tag.
        """
        return self.model.objects

    def get_queryset(self):
        """
        Build queryset base to list Tag articles.

        Depend on "self.object" to list the Tag related objects.
        """
        q = self.apply_article_lookups(
            self.listed_model.objects.filter(
                tags__id__in=[self.object.id]
            ),
            self.request.LANGUAGE_CODE,
        )

        return q.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get(self, request, *args, **kwargs):
        # Try to get Tag object
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        # Let the ListView mechanics manage list pagination from given queryset
        return super().get(request, *args, **kwargs)


TagIndexView = type("TagIndexView", (
    (EnabledTagIndexView,)
    if settings.LOTUS_ENABLE_TAG_INDEX_VIEW
    else (DisabledTagIndexView,)
), {})
"""
This is the effective index class view which inherit either from the working index view
or the dummy 404 view Tag index is enabled or not according to settings.
"""
