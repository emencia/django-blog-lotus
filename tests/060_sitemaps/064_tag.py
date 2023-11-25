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
from django.urls import reverse, translate_url

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, TagFactory
from lotus.sitemaps import TagSitemap
from lotus.utils.jsons import ExtendedJsonEncoder


@freeze_time("2012-10-15 10:00:00")
def test_tagsitemap_publication(db, client, rf):
    """
    Tag sitemap lists all active tag for each available languages.
    """
    current_site = Site.objects.get_current()

    utc = ZoneInfo("UTC")
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    science = TagFactory(name="Science", slug="science")
    sausage = TagFactory(name="Sausage", slug="sausage")
    TagFactory(name="Not used", slug="not-used")

    ArticleFactory(title="Foo", fill_tags=[science])
    ArticleFactory(title="Bar", fill_tags=[science])

    # Unavailable articles to anonymous
    ArticleFactory(
        title="France",
        fill_tags=[science],
        language="fr",
    )
    # Unavailable articles to anonymous
    ArticleFactory(
        title="Ping",
        fill_tags=[science],
        status=STATUS_DRAFT,
    )
    ArticleFactory(
        title="Pong",
        fill_tags=[science],
        private=True,
    )
    ArticleFactory(
        title="Pang",
        fill_tags=[science],
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    ArticleFactory(
        title="Nope",
        fill_tags=[sausage],
    )

    sitemap = TagSitemap()
    page = rf.get("/").GET.get("p", 1)
    urls = sitemap.get_urls(page=page, site=current_site, protocol="http")

    # print()
    # print(json.dumps(urls, indent=4, cls=ExtendedJsonEncoder))
    # print()
    payload = json.loads(
        json.dumps(urls, indent=4, cls=ExtendedJsonEncoder)
    )

    # Serialize urls payload using a JSON transition
    assert payload == [
        {
            "item": "<Tag: Sausage>",
            "location": "http://example.com/en/tags/sausage/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Tag: Science>",
            "location": "http://example.com/en/tags/science/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Tag: Science>",
            "location": "http://example.com/fr/tags/science/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_tagsitemap_xml(db, client):
    """
    Basic test to check XML response is correct.
    """
    current_site = Site.objects.get_current()
    base_url = "http://{}".format(current_site.domain)

    utc = ZoneInfo("UTC")
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    science = TagFactory(name="Science", slug="science")
    sausage = TagFactory(name="Sausage", slug="sausage")
    TagFactory(name="Not used", slug="not-used")

    ArticleFactory(title="Foo", fill_tags=[science])
    ArticleFactory(title="Bar", fill_tags=[science])

    # Unavailable articles to anonymous
    ArticleFactory(
        title="France",
        fill_tags=[science],
        language="fr",
    )
    # Unavailable articles to anonymous
    ArticleFactory(
        title="Ping",
        fill_tags=[science],
        status=STATUS_DRAFT,
    )
    ArticleFactory(
        title="Pong",
        fill_tags=[science],
        private=True,
    )
    ArticleFactory(
        title="Pang",
        fill_tags=[science],
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    ArticleFactory(
        title="Nope",
        fill_tags=[sausage],
    )

    expected_urls = [
        base_url + reverse("lotus:tag-detail", kwargs={"tag": sausage.slug}),
        base_url + reverse("lotus:tag-detail", kwargs={"tag": science.slug}),
        base_url + translate_url(
            reverse("lotus:tag-detail", kwargs={"tag": science.slug}),
            "fr"
        ),
    ]

    url = reverse("django.contrib.sitemaps.views.sitemap", kwargs={
        "section": "lotus-tag",
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
