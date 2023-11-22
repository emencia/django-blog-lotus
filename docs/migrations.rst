.. _migrate_intro:

==========
Migrations
==========

From 0.7.0 to 0.8.0
*******************

New feature Album
    * If you use a custom template for Article detail view you will need to update it
      to include the `Album part <https://github.com/emencia/django-blog-lotus/blob/v0.8.0/lotus/templates/lotus/article/detail.html#L34>`_;
    * If you copied the Sass sources frontend, you will need to update Bootstrap settings to
      `enable the CSS Grid <https://github.com/emencia/django-blog-lotus/blob/v0.8.0/frontend/scss/settings/_bootstrap.scss#L9>`_
      with ``$enable-cssgrid: true;``;
    * A new setting ``LOTUS_ALBUM_TAG_TEMPLATE`` is required, see
      :ref:`intro_install_settings` documentation if you don't import the default
      settings from Lotus;

New feature Canonical URL
    * You need to add ``django.contrib.sites.middleware.CurrentSiteMiddleware`` middleware
      to your ``settings.MIDDLEWARES``;
    * A new template block ``{% block header-resource-extra %}`` has to be added in
      `template skeleton <https://github.com/emencia/django-blog-lotus/blob/v0.8.0/sandbox/templates/skeleton.html#L14>`_
      since Lotus use in its templates;
    * If you use a custom ``lotus/base.html`` you will need to update it to include
      the `new part which build the canonical URL <https://github.com/emencia/django-blog-lotus/blob/v0.8.0/lotus/templates/lotus/base.html#L3>`_;

CKEditor integration
    In our sandbox settings we enabled the plugin ``image2`` instead of default image
    plugin since it has a minor ergonomy improvement, you may include it also in your
    CKEditor configuration with the
    `following two lines <https://github.com/emencia/django-blog-lotus/blob/v0.8.0/sandbox/settings/base.py#L190>`_;

Admin improvements
    New settings ``LOTUS_ADMIN_ARTICLE_ASSETS``, ``LOTUS_ADMIN_CATEGORY_ASSETS``
    and ``LOTUS_ADMIN_ALBUM_ASSETS``  are required, see
    :ref:`intro_install_settings` documentation if you don't import the default
    settings from Lotus;


From 0.6.1 to 0.7.0
*******************

Improved related article in Article detail view
    If you were using a custom template for Article details and keeped the part for
    related article listing that was starting with
    ``{% with relateds=article_object.get_related %}`` you must change it to use the
    new template tag which apply the publication and language filtering.

    See the
    `current detail template <https://github.com/emencia/django-blog-lotus/blob/v0.7.0/lotus/templates/lotus/article/detail.html#L169>`_
    to know what to copy. This is important since the old template only applied language
    filtering and totally ignore publication criterias;

New feature API
    You may now enable the API with installing package extra requirement ``api`` and
    then follow install guide about :ref:`install_api`;


From 0.6.0 to 0.6.1
*******************

Nothing to do, this is a minor maintenance release about documentation build on
readthedocs.


From 0.5.2.1 to 0.6.0
*********************

* Upgrade ``django-autocomplete-light``;
* Use the new template block names if you override some of lotus list or details
  templates;

  * ``head_title`` to ``header-title``;
  * ``head_metas`` to ``metas``;
  * ``head_styles`` to ``header-resource``;
  * ``javascript`` to ``body-javascript``;

* If you mounted Lotus on root url path and standing on removed ``articles/`` path to
  not pollute root path, you need to mount Lotus on path like ``blog/`` or even
  ``articles/``;
* If you used Lotus for a single language site, now you may be able to disable
  ``LocaleMiddleware``;
* Now you are able to edit Lotus crumb titles for index views, see settings
  documentation for ``LOTUS_CRUMBS_TITLES``;
