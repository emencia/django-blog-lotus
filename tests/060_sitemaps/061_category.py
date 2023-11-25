import json

import lxml.etree
from freezegun import freeze_time

from django.contrib.sites.models import Site
from django.urls import reverse

from lotus.factories import CategoryFactory
from lotus.sitemaps import CategorySitemap
from lotus.utils.jsons import ExtendedJsonEncoder


@freeze_time("2012-10-15 10:00:00")
def test_categorysitemap_publication(db, client, rf):
    """
    Category sitemap list all objects and with translation mode enabled only originals
    are listed and include their possible translations as alternate items.
    """
    current_site = Site.objects.get_current()

    cheese = CategoryFactory(title="Cheese", slug="cheese")
    CategoryFactory(title="Pudding", slug="pudding")
    CategoryFactory(title="Fromage", slug="fromage", language="fr", original=cheese)
    CategoryFactory(title="Baguette", slug="baguette", language="fr")

    sitemap = CategorySitemap()
    page = rf.get("/").GET.get("p", 1)
    urls = sitemap.get_urls(page=page, site=current_site, protocol="http")

    payload = json.loads(
        json.dumps(urls, indent=4, cls=ExtendedJsonEncoder)
    )

    # Serialize urls payload using a JSON transition
    assert payload == [
        {
            "item": "<Category: Baguette>",
            "location": "http://example.com/fr/categories/baguette/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Category: Cheese>",
            "location": "http://example.com/en/categories/cheese/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": [
                {
                    "location": "http://example.com/fr/categories/fromage/",
                    "lang_code": "fr"
                }
            ]
        },
        {
            "item": "<Category: Pudding>",
            "location": "http://example.com/en/categories/pudding/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_categorysitemap_no_alternates(db, client, rf):
    """
    When translation mode is disabled, both original and translation objects are listed
    without alternate items.
    """
    current_site = Site.objects.get_current()

    cheese = CategoryFactory(title="Cheese", slug="cheese")
    CategoryFactory(title="Pudding", slug="pudding")
    CategoryFactory(title="Fromage", slug="fromage", language="fr", original=cheese)
    CategoryFactory(title="Baguette", slug="baguette", language="fr")

    class FlatCategorySitemap(CategorySitemap):
        # Custom class to disallow transition mode
        translations = False

    sitemap = FlatCategorySitemap()
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
            "item": "<Category: Baguette>",
            "location": "http://example.com/fr/categories/baguette/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Category: Cheese>",
            "location": "http://example.com/en/categories/cheese/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Category: Fromage>",
            "location": "http://example.com/fr/categories/fromage/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Category: Pudding>",
            "location": "http://example.com/en/categories/pudding/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_categorysitemap_xml(db, client):
    """
    Basic test to check XML response is correct.
    """
    current_site = Site.objects.get_current()
    base_url = "http://{}".format(current_site.domain)

    cheese = CategoryFactory(title="Cheese", slug="cheese")
    pudding = CategoryFactory(title="Pudding", slug="pudding")
    baguette = CategoryFactory(title="Baguette", slug="baguette", language="fr")
    fromage = CategoryFactory(
        title="Fromage",
        slug="fromage",
        language="fr",
        original=cheese
    )

    url = reverse("django.contrib.sitemaps.views.sitemap", kwargs={
        "section": "lotus-category",
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

    assert found_urls == [
        base_url + baguette.get_absolute_url(),
        base_url + cheese.get_absolute_url(),
        base_url + pudding.get_absolute_url(),
    ]

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
        ("fr", base_url + fromage.get_absolute_url()),
    ]
