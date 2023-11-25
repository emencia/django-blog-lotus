import json

import lxml.etree
from freezegun import freeze_time

from django.contrib.sites.models import Site
from django.urls import reverse, translate_url

from lotus.choices import STATUS_DRAFT
from lotus.factories import ArticleFactory, AuthorFactory
from lotus.sitemaps import AuthorSitemap
from lotus.utils.jsons import ExtendedJsonEncoder


@freeze_time("2012-10-15 10:00:00")
def test_authorsitemap_publication(db, client, rf):
    """
    Author sitemap lists all active author for each available languages.
    """
    current_site = Site.objects.get_current()

    carl_barks = AuthorFactory(
        first_name="Carl",
        last_name="Barks",
        username="carl-barks"
    )
    don_rosa = AuthorFactory(
        first_name="Don",
        last_name="Rosa",
        username="don-rosa"
    )
    jules_verne = AuthorFactory(
        first_name="Jules",
        last_name="Verne",
        username="jules-verne"
    )
    niet = AuthorFactory(
        first_name="niet",
        last_name="Niet",
        username="Niet"
    )
    spy = AuthorFactory(
        first_name="James",
        last_name="Bond",
        username="spy"
    )

    # Author need at least a published article to be "active"
    ArticleFactory(title="Sample", fill_authors=[carl_barks, jules_verne])
    ArticleFactory(title="Exemple", language="fr", fill_authors=[jules_verne])

    # Related author won't be active with no published articles, also we mix with
    # proper active authors to check false negatives
    ArticleFactory(title="Nope", status=STATUS_DRAFT, fill_authors=[niet, carl_barks])
    ArticleFactory(title="Private", private=True, fill_authors=[spy, don_rosa])

    sitemap = AuthorSitemap()
    page = rf.get("/").GET.get("p", 1)
    urls = sitemap.get_urls(page=page, site=current_site, protocol="http")

    payload = json.loads(
        json.dumps(urls, indent=4, cls=ExtendedJsonEncoder)
    )

    # Serialize urls payload using a JSON transition
    assert payload == [
        {
            "item": "<Author: Carl Barks>",
            "location": "http://example.com/en/authors/carl-barks/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Author: Jules Verne>",
            "location": "http://example.com/en/authors/jules-verne/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        },
        {
            "item": "<Author: Jules Verne>",
            "location": "http://example.com/fr/authors/jules-verne/",
            "lastmod": "2012-10-15T10:00:00+00:00",
            "changefreq": "monthly",
            "priority": "0.5",
            "alternates": []
        }
    ]


@freeze_time("2012-10-15 10:00:00")
def test_authorsitemap_xml(db, client):
    """
    Basic test to check XML response is correct.
    """
    current_site = Site.objects.get_current()
    base_url = "http://{}".format(current_site.domain)

    carl_barks = AuthorFactory(
        first_name="Carl",
        last_name="Barks",
        username="carl-barks"
    )
    don_rosa = AuthorFactory(
        first_name="Don",
        last_name="Rosa",
        username="don-rosa"
    )
    jules_verne = AuthorFactory(
        first_name="Jules",
        last_name="Verne",
        username="jules-verne"
    )
    niet = AuthorFactory(
        first_name="niet",
        last_name="Niet",
        username="Niet"
    )
    spy = AuthorFactory(
        first_name="James",
        last_name="Bond",
        username="spy"
    )

    # Author need at least a published article to be "active"
    ArticleFactory(title="Sample", fill_authors=[carl_barks, jules_verne])
    ArticleFactory(title="Exemple", language="fr", fill_authors=[jules_verne])

    # Related author won't be active with no published articles, also we mix with
    # proper active authors to check false negatives
    ArticleFactory(title="Nope", status=STATUS_DRAFT, fill_authors=[niet, carl_barks])
    ArticleFactory(title="Private", private=True, fill_authors=[spy, don_rosa])

    expected_urls = [
        base_url + carl_barks.get_absolute_url(),
        base_url + jules_verne.get_absolute_url(),
        base_url + translate_url(jules_verne.get_absolute_url(), "fr"),
    ]

    url = reverse("django.contrib.sitemaps.views.sitemap", kwargs={
        "section": "lotus-author",
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
