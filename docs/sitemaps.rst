.. _XML sitemap format: https://www.sitemaps.org/
.. _Google sitemap XML: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap?hl=en#xml
.. _Django sitemap framework: https://docs.djangoproject.com/en/stable/ref/contrib/sitemaps/

.. _sitemaps_intro:

===========
Sitemap XML
===========

Sitemap are XML files following the `XML sitemap format`_ and endorsed by search tools
(like `Google sitemap XML`_) to improve your SEO on contents.

Lotus implements Sitemap classes for Article, Category, Author and Tag content types.

.. _install_sitemaps:

Install
*******

You just need to enable the `Django sitemap framework`_ in enabled applications before
the line for Lotus: ::

    INSTALLED_APPS = (
        ...
        "django.contrib.sitemaps",
        ...
        "lotus",
    )


Options
*******

Each included sitemap class support some options that can be defined from settings.
From default Lotus settings classes just define ``changefreq`` to ``monthly`` and
``priority`` to ``0.5``, see :ref:`intro_install_settings` for a detail of supported
options.


.. _sitemaps_translation_mode:

Translation mode
----------------

Default Django Sitemap way to support translation is just to prefix the same url with
language code. Like for exemple an english object with URL
``http://foo.com/en/cheese/`` and enabled english and french languages it would results
on something like this: ::

   <url>
      <loc>http://foo.com/en/cheese/</loc>
      <xhtml:link rel="alternate" hreflang="fr" href="http://foo.com/fr/cheese/" />
   </url>

But Lotus translations are different objects with their own slug and URL, so our Sitemap
classes with translated objects have the translation mode enabled on default to endorse
this specifity.

This mode will only list original objects then add their possible
translations as ``alternate`` items with their own URL: ::

   <url>
      <loc>http://foo.com/en/cheese/</loc>
      <xhtml:link rel="alternate" hreflang="fr" href="http://foo.com/fr/fromage/" />
   </url>

If this is not your expected behavior, you may disable this mode and it will just list
every objects: ::

   <url>
      <loc>http://foo.com/en/cheese/</loc>
   </url>
   <url>
      <loc>http://foo.com/fr/fromage/</loc>
   </url>


Publish
*******

At this point no sitemap are published yet since Lotus let you do it yourself. This is
because you may not want to enable every content sitemap, sometime you may not want to
publish a sitemap for tags or authors.

There is also some options for each sitemap you would want to adjust for your SEO
strategy.

We recommend to publish a sitemap per content type with an index: ::

    from django.contrib.sitemaps import views as sitemap_views
    from django.urls import path

    from lotus.sitemaps import ArticleSitemap, AuthorSitemap, CategorySitemap, TagSitemap

    # Enabled sitemap classes with their section name
    sitemap_classes = {
        "lotus-article": ArticleSitemap,
        "lotus-author": AuthorSitemap,
        "lotus-category": CategorySitemap,
        "lotus-tag": TagSitemap,
    }

    urlpatterns = [
        ...
        path("sitemap.xml", sitemap_views.index, {"sitemaps": sitemap_classes}),
        path(
            "sitemap-<section>.xml",
            sitemap_views.sitemap,
            {"sitemaps": sitemap_classes},
            name="django.contrib.sitemaps.views.sitemap"
        ),
    ]

This will publish a ``/sitemap.xml`` which is an index of available content sitemaps,
in this configuration you will get ``/sitemap-lotus-article.xml`` for the Article
sitemap and the same kind of URLs for Author, Category and Tag sitemaps.

.. Hint::
    This is just a recommendation and finally you can use the Lotus sitemap classes as
    you want, see `Django sitemap framework`_ documentation to know how the sitemap
    classes and views are working.