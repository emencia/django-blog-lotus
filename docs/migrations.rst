.. _migrate_intro:

==========
Migrations
==========


From 0.9.4 to 0.9.5
*******************

This is a minor release for a fix with
`custom User model <https://docs.djangoproject.com/en/stable/topics/auth/customizing/>`_.

It includes an update of the initial Lotus migration but is totally safe for both
existing and new projects.


From 0.9.3.1 to 0.9.4
*********************

This is a minor release for the new feature of custom templates for Article and Category
detail views.

If you were using the default Lotus settings, you are safe to migrate without any
change. Else your project explicitely defines all Lotus settings you will jsut have to
include the new ones: ``LOTUS_ARTICLE_DETAIL_TEMPLATES`` and
``LOTUS_CATEGORY_DETAIL_TEMPLATES``.


From 0.9.2 to 0.9.3
*******************

This is a minor maintenance release without any changes on features or behaviors,
you should be able to migrate safely.

* You can upgrade your project to Django 5.2 if you want;
* You can upgrade your project to Bootstrap 5.3.6 if you want;
* You can upgrade your project to djangorestframework 3.16.0 if you want;
* Be advised that Django 5.2 requires Python>=3.10;
* Be advised that djangorestframework 3.16.0 requires Django>=4.2;


From 0.9.1 to 0.9.2
*******************

* You can upgrade your project to Django>=5.0 if you want;
* We relaxed **django-taggit** requirement to fit to **Django>=5.0** support. If your
  are still using **Django 3.2** you will need to force install of
  'django-taggit<5.0.0' before Lotus because 'django-taggit>=5.0.0' is not compatible
  with 'Django 3.2';
* Be advised that Django>=5.0 requires Python>=3.10;


From 0.9.0 to 0.9.1
*******************

This is a minor maintenance release without incompatible changes, you may however look
at setting ``LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE`` documentation if you are using API
and prefer to still on old detail endpoints behavior.


From 0.8.1 to 0.9.0
*******************

New feature 'Category tree'
    Updating to this new release will install **django-treebeard** and new migrations.

    You must proceed to in order:

    #. Upgrade to the Lotus 0.9.0, this will install dependency to **django-treebeard**;
    #. You must add ``django-treebeard`` in setting ``INSTALLED_APPS``, preferably after
       ``dal`` and before ``lotus``, you can see a proper sample in
       :ref:`install_config_from_scratch`;
    #. Apply new migrations;
    #. Update your category detail template;
    #. If you use a custom template for Category detail view you will need to update it
       to include the new `Subcategories part <https://github.com/emencia/django-blog-lotus/blob/v0.9.0/lotus/templates/lotus/category/detail.html#L71>`_ and its related `fragment to list subcategories <https://github.com/emencia/django-blog-lotus/blob/v0.9.0/lotus/templates/lotus/category/partials/subcategories.html>`_ and possibly a minor fix around `Article listing part <https://github.com/emencia/django-blog-lotus/blob/v0.9.0/lotus/templates/lotus/category/detail.html#L30>`_. However this is not a breaking change and everything should work without it, just you won't benefit from Category tree feature;

    Finally if your project is customizing Django admin, you may look into
    `last changes on Lotus admin <https://github.com/emencia/django-blog-lotus/blob/v0.9.0/lotus/templates/admin/lotus/category/change_list.html>`_
    templates that may have changed a little bit to include a link for
    the Category tree and some new Category fields.


From 0.8.0 to 0.8.1
*******************

New migration
    A new basic model migration has been added to add a ``modified`` field on some
    models, you just have to apply it on your project.

New feature 'Sitemap'
    This new feature is available but you will need to enable it, see install guide in
    documentation Sitemap :ref:`install_sitemaps`.


From 0.7.0 to 0.8.0
*******************

New feature 'Album'
    * If you use a custom template for Article detail view you will need to update it
      to include the `Album part <https://github.com/emencia/django-blog-lotus/blob/v0.8.0/lotus/templates/lotus/article/detail.html#L34>`_;
    * If you copied the Sass sources frontend, you will need to update Bootstrap settings to
      `enable the CSS Grid <https://github.com/emencia/django-blog-lotus/blob/v0.8.0/frontend/scss/settings/_bootstrap.scss#L9>`_
      with ``$enable-cssgrid: true;``;
    * A new setting ``LOTUS_ALBUM_TAG_TEMPLATE`` is required, see
      :ref:`intro_install_settings` documentation if you don't import the default
      settings from Lotus;

New feature 'Canonical URL'
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
    If you were using a custom template for Article details and retained the part for
    the related article listing that began with
    ``{% with relateds=article_object.get_related %}``, you must modify it to utilize
    the new template tag. This new tag applies both publication and language filtering.

    Refer to the `current detail template <https://github.com/emencia/django-blog-lotus/blob/2774ca69af7d9acfa6dc77ac0bf7549bcd62779e/lotus/templates/lotus/article/detail.html#L169>`_
    to determine what to copy. This modification is vital since the old template applied
    only language filtering and completely disregarded publication criteria.

New feature 'API'
    You may now enable the API with installing package extra requirement ``api`` and
    then follow install guide about API :ref:`install_api`;


From 0.6.0 to 0.6.1
*******************

Nothing to do here, this is a minor maintenance release focused on documentation build
for readthedocs.


From 0.5.2.1 to 0.6.0
*********************

* Upgrade ``django-autocomplete-light``;
* Adjust to the new template block names if you have overridden any of Lotus list or
  detail templates:

  * ``head_title`` to ``header-title``;
  * ``head_metas`` to ``metas``;
  * ``head_styles`` to ``header-resource``;
  * ``javascript`` to ``body-javascript``;

* If you had mounted Lotus on the root URL path and relied on the now-removed
  ``articles/`` path to avoid cluttering the root, you should remount Lotus on paths
  like ``blog/`` or ``articles/``;
* If you used Lotus for a single language site, you might now have the option to
  disable ``LocaleMiddleware`` middleware;
* You can now edit Lotus breadcrumb titles for index views. Consult the settings
  documentation for ``LOTUS_CRUMBS_TITLES``.
