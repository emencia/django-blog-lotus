from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Q
from django.http import Http404, HttpResponseBadRequest
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.views import View

from dal import autocomplete
from taggit.models import Tag

from ..models import Article
from .mixins import ArticleFilterAbstractView

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


class EnabledTagIndexView(BaseBreadcrumbMixin, ArticleFilterAbstractView, ListView):
    """
    List of tags that are related from at least one article.
    """
    model = Tag
    template_name = "lotus/tag/list.html"
    paginate_by = settings.LOTUS_TAG_PAGINATION
    context_object_name = "tag_list"
    crumb_title = settings.LOTUS_CRUMBS_TITLES["tag-index"]
    crumb_urlname = "lotus:tag-index"
    lotus_stage = "tags"

    @property
    def crumbs(self):
        return [
            (self.crumb_title, reverse(self.crumb_urlname)),
        ]

    def get_queryset(self):
        """
        Build complex queryset to get all tags which have published articles.

        Published articles are determined with the common publication criterias.
        """
        publication_criterias = self.build_article_lookups(
            language=self.get_language_code(),
            prefix="article__",
        )

        return Tag.objects.annotate(
            article_count=Count(
                "article",
                filter=Q(*publication_criterias),
            )
        ).filter(article_count__gt=0).order_by("name")


class TagDetailView(BaseBreadcrumbMixin, ArticleFilterAbstractView,
                    SingleObjectMixin, ListView):
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
            self.get_language_code(),
        )

        return q.order_by(*self.listed_model.COMMON_ORDER_BY)

    def get(self, request, *args, **kwargs):
        # Try to get Tag object
        self.object = self.get_object(queryset=self.get_queryset_for_object())

        # Let the ListView mechanics manage list pagination from given queryset
        return super().get(request, *args, **kwargs)


class TagAutocompleteView(UserPassesTestMixin, autocomplete.Select2QuerySetView):
    """
    View to return JSON response for a tag list.

    Default returns paginated list of all available tags. If request argument ``q`` is
    given, the list will return tag items that start with text from argument.

    Worth to notice this is language agnostic, since a Tag does not have any specific
    language.
    """
    def test_func(self):
        """
        Limit to admin only
        """
        return self.request.user.is_staff

    def get_queryset(self):
        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs.order_by("name")

    def post(self, request, *args, **kwargs):
        """
        POST request is forbidden since DAL would create a tag for a missing value.
        """
        return HttpResponseBadRequest()


TagIndexView = type("TagIndexView", (
    (EnabledTagIndexView,)
    if settings.LOTUS_ENABLE_TAG_INDEX_VIEW
    else (DisabledTagIndexView,)
), {})
"""
This is the effective index class view which inherit either from the working index view
or the dummy 404 view if Tag index is enabled or not according to settings.
"""
