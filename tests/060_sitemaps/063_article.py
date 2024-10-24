import datetime
import json

import lxml.etree
from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.contrib.sites.models import Site
from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory
from lotus.sitemaps import ArticleSitemap
from lotus.utils.jsons import ExtendedJsonEncoder


@freeze_time("2012-10-15 10:00:00")
def test_articlesitemap_publication(db, client, rf):
    """
    Article sitemap only list object that can be reached by anonymous and with
    translation mode enabled only originals are listed and include their possible
    translations as alternate items.
    """
    current_site = Site.objects.get_current()

    # Date references
    utc = ZoneInfo("UTC")
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=utc)
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    ArticleFactory(
        title="draft",
        slug="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    published_yesterday = ArticleFactory(
        title="published yesterday",
        slug="yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    ArticleFactory(
        title="not yet published",
        slug="not-yet-published",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    ArticleFactory(
        title="french original",
        slug="french-original",
        publish_date=today.date(),
        publish_time=today.time(),
        language="fr",
    )
    ArticleFactory(
        original=published_yesterday,
        title="publié hier",
        slug="publie-hier",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        language="fr",
    )

    sitemap = ArticleSitemap()
    page = rf.get("/").GET.get("p", 1)
    urls = sitemap.get_urls(page=page, site=current_site, protocol="http")

    payload = json.loads(
        json.dumps(urls, indent=4, cls=ExtendedJsonEncoder)
    )

    # Serialize urls payload using a JSON transition
    assert payload == [
        {
            "item": "<Article: french original>",
            "location": "http://example.com/fr/2012/10/15/french-original/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.51",
            "alternates": []
        },
        {
            "item": "<Article: published yesterday>",
            "location": "http://example.com/en/2012/10/14/yesterday/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.51",
            "alternates": [
                {
                    "location": "http://example.com/fr/2012/10/14/publie-hier/",
                    "lang_code": "fr"
                }
            ]
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_articlesitemap_no_alternates(db, client, rf):
    """
    When translation mode is disabled, both original and translation objects are listed
    without alternate items.
    """
    current_site = Site.objects.get_current()

    # Date references
    utc = ZoneInfo("UTC")
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=utc)
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    ArticleFactory(
        title="draft",
        slug="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    published_yesterday = ArticleFactory(
        title="published yesterday",
        slug="yesterday",
        pinned=True,
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    ArticleFactory(
        title="not yet published",
        slug="not-yet-published",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    ArticleFactory(
        title="french original",
        slug="french-original",
        publish_date=today.date(),
        publish_time=today.time(),
        language="fr",
    )
    ArticleFactory(
        original=published_yesterday,
        title="publié hier",
        slug="publie-hier",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        language="fr",
    )

    class FlatArticleSitemap(ArticleSitemap):
        # Custom class to disallow transition mode
        translations = False

    sitemap = FlatArticleSitemap()
    page = rf.get("/").GET.get("p", 1)
    urls = sitemap.get_urls(page=page, site=current_site, protocol="http")

    payload = json.loads(
        json.dumps(urls, indent=4, cls=ExtendedJsonEncoder)
    )

    # Serialize urls payload using a JSON transition
    assert payload == [
        {
            "item": "<Article: french original>",
            "location": "http://example.com/fr/2012/10/15/french-original/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.51",
            "alternates": []
        },
        {
            "item": "<Article: published yesterday>",
            "location": "http://example.com/en/2012/10/14/yesterday/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.8",
            "alternates": []
        },
        {
            "item": "<Article: publié hier>",
            "location": "http://example.com/fr/2012/10/14/publie-hier/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.51",
            "alternates": []
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_articlesitemap_xml(db, client):
    """
    Basic test to check XML response is correct.
    """
    current_site = Site.objects.get_current()
    base_url = "http://{}".format(current_site.domain)

    # Date references
    utc = ZoneInfo("UTC")
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=utc)
    yesterday = datetime.datetime(2012, 10, 14, 10, 0).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    ArticleFactory(
        title="draft",
        slug="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    published_yesterday = ArticleFactory(
        title="published yesterday",
        slug="yesterday",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
    )
    ArticleFactory(
        title="not yet published",
        slug="not-yet-published",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    french = ArticleFactory(
        title="french original",
        slug="french-original",
        publish_date=today.date(),
        publish_time=today.time(),
        language="fr",
    )
    french_published_yesterday = ArticleFactory(
        original=published_yesterday,
        title="publié hier",
        slug="publie-hier",
        publish_date=yesterday.date(),
        publish_time=yesterday.time(),
        language="fr",
    )

    expected_urls = [
        base_url + french.get_absolute_url(),
        base_url + published_yesterday.get_absolute_url(),
    ]

    url = reverse("django.contrib.sitemaps.views.sitemap", kwargs={
        "section": "lotus-article",
    })
    response = client.get(url)
    assert response.status_code == 200

    # Parse XML to get url items
    tree = lxml.etree.fromstring(response.content)
    found_urls = [
        url
        for url in tree.xpath("//urlset:loc/text()", namespaces={
            "urlset": "http://www.sitemaps.org/schemas/sitemap/0.9",
        })
    ]

    assert found_urls == expected_urls

    # Parse XML to get alternate urls (directly without checking for path of
    # alternate items against original parent)
    found_alternates = [
        (alt.get("hreflang"), alt.get("href"))
        for alt in tree.xpath("//urlset:url/xhtml:link[@rel='alternate']", namespaces={
            "urlset": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "xhtml": "http://www.w3.org/1999/xhtml",
        })
    ]

    assert found_alternates == [
        ("fr", base_url + french_published_yesterday.get_absolute_url()),
    ]
