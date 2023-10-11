.. _migrate_intro:

==========
Migrations
==========

From 0.6.1 to 0.7.0
*******************

* If you were using a custom template for Article details and keeped the part for
  related article listing that was starting with
  ``{% with relateds=article_object.get_related %}`` you must change it to use the
  new template tag which apply the publication and language filtering. See the
  `current detail template <https://github.com/emencia/django-blog-lotus/blob/2774ca69af7d9acfa6dc77ac0bf7549bcd62779e/lotus/templates/lotus/article/detail.html#L169>`_
  to know what to copy. This is important since the old template only applied language
  filtering and totally ignore publication criterias;
* You may now enable the API with installing package extra requirement ``api`` and
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
