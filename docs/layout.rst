.. _layout_intro:

======
Layout
======

Assets
******

Every included templates have been made for Bootstrap v5 components but the packaged
application does not provide any assets.

You may simply retrieve these assets from
`Bootstrap CDN or download precompiled assets <https://getbootstrap.com/docs/5.2/getting-started/download/>`_
(CSS and Javascript) from Bootstrap itself. Here are the versions you will have to use:

* Bootstrap 5.2.3;
* Bootstrap-icons 1.8.0;

However there is only a very few CSS enhancements around states icons, that you could
just start on your own Bootstrap v5 build. Or you can just copy the
`demonstration frontend <https://github.com/emencia/django-blog-lotus/tree/master/frontend>`_
into your project.

Templates
*********

Template integration is pretty basic and just focus to properly demonstrate Lotus
behaviors and features with basic Bootstrap components usage.

Finally every HTML part is built from a template and you can override all of them to
include you very specific layout design with or without Bootstrap.

For more details on template integration you could see references on
:ref:`references_templatetags_intro` and :ref:`references_views_intro`.

Details templates
-----------------

Article and Category objects can select a template to render their detail view.

The list of available template choices is defined from settings
``LOTUS_ARTICLE_DETAIL_TEMPLATES`` and ``LOTUS_CATEGORY_DETAIL_TEMPLATES`` that you
can alter from your project settings. The first item of these choices are assumed
to be the default one.

.. Warning::
    These choices list are not validated against existing objects or migrations, if
    you remove a template path that is already used from objects you will have an error
    from detail view rendering, be careful about it.
