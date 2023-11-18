import datetime

from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.contrib.auth.models import AnonymousUser
from django.template import Context

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory
from lotus.templatetags.lotus import article_get_related
from lotus.views.mixins import ArticleFilterAbstractView


@freeze_time("2012-10-15 10:00:00")
def test_tag_get_related_render(db, settings, rf):
    """
    Tag "article_get_related" should either list all related article objects if there
    is no filtering function given, or list only objects that match filter function.
    """
    settings.LANGUAGE_CODE = "en"

    # Craft a proper view class with a request and that can be used to give
    # a working filtering function
    filternator = ArticleFilterAbstractView()
    filternator.request = rf.get("/")
    filternator.request.user = AnonymousUser()

    # Date references
    utc = ZoneInfo("UTC")
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=utc)
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    draft = ArticleFactory(
        title="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    published_yesterday = ArticleFactory(
        title="published yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    published_notyet = ArticleFactory(
        title="not yet published",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    french = ArticleFactory(
        title="french",
        publish_date=today.date(),
        publish_time=today.time(),
        language="fr",
    )

    article = ArticleFactory(
        title="basic published",
        publish_date=today.date(),
        publish_time=today.time(),
        fill_related=[draft, published_yesterday, published_notyet, french],
    )

    # Without filtering function in context, tag will return all objects for current
    # language
    relateds = article_get_related(Context(), article)
    assert sorted([item.title for item in relateds]) == [
        "draft",
        "not yet published",
        "published yesterday"
    ]

    # With filtering function in context, tag will return objects filtered on all
    # criterias
    relateds = article_get_related(
        Context({"article_filter_func": filternator.apply_article_lookups}),
        article
    )
    assert sorted([item.title for item in relateds]) == ["published yesterday"]
