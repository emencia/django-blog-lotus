.. _migrate_intro:

==========
Migrations
==========

From 0.6.1 to 0.7.0
*******************

* If you were using a custom template for Article details and retained the part for
  the related article listing that began with
  ``{% with relateds=article_object.get_related %}``, you must modify it to utilize 
  the new template tag. This new tag applies both publication and language filtering.
  Refer to the `current detail template <https://github.com/emencia/django-blog-lotus/blob/2774ca69af7d9acfa6dc77ac0bf7549bcd62779e/lotus/templates/lotus/article/detail.html#L169>`_
  to determine what to copy. This modification is vital since the old template applied
  only language filtering and completely disregarded publication criteria.

* You can now activate the API by installing the extra package requirement ``api`` and
then following the installation guide for :ref:`install_api`;

From 0.6.0 to 0.6.1
*******************

Nothing to do here, this is a minor maintenance release focused on documentation
 build for readthedocs.

From 0.5.2.1 to 0.6.0
*********************

* Upgrade ``django-autocomplete-light>=3.9.7``.
  
* Adjust to the new template block names if you have overridden any of Lotus's list or detail templates:

  * ``head_title`` to ``header-title``;
  * ``head_metas`` to ``metas``;
  * ``head_styles`` to ``header-resource``;
  * ``javascript`` to ``body-javascript``;

* If you had mounted Lotus on the root URL path and relied on the now-removed ``articles/``
  path to avoid cluttering the root, you should remount Lotus on paths like ``blog/`` or ``articles/``.
  
* If you used Lotus for a single-language site, you might now have the option to disable ``LocaleMiddleware``.

* You can now edit Lotus breadcrumb titles for index views. Consult the settings documentation for ``LOTUS_CRUMBS_TITLES``.
