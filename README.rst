.. _Python: https://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _django-ckeditor: https://github.com/django-ckeditor/django-ckeditor
.. _django-view-breadcrumbs: https://github.com/tj-django/django-view-breadcrumbs

=================
Django Blog Lotus
=================

A weblog application with Django.

This is on alpha stage, everything is working but expected basic behaviors may not be
finished yet. Full documentation is yet to be done.

Dependancies
************

* `Python`_>=3.8;
* `Django`_>=3.2;
* `django-ckeditor`_>=6.0.0;
* `django-view-breadcrumbs`_>=2.2.1 (optional);

Links
*****

* (Not yet) Read the documentation on `Read the docs <https://django-blog-lotus.readthedocs.io/>`_;
* (Not yet) Download its `PyPi package <https://pypi.python.org/pypi/django-blog-lotus>`_;
* Clone it on its `Github repository <https://github.com/emencia/django-blog-lotus>`_;

Differences with Zinnia
***********************

Some of Zinnia features have been dropped:

* Category have no more "tree" levels feature;
* All features related to "discussion" (pingback, comments, etc..);
* Custom templates for each Article;
* Multi-sites (Django Site framework) article support;
* There is no more a distinct publication date and publication start. Now
  publication start is the publication date;
* Article status is limited to "draft" or "available";
* There is no "short url" feature;
* Article image caption;
* Article tags;
* Article password;
* Article modularity which enabled to use a custom Article model instead of
  shipped one;

Additional features:

* Multi-lingual content;
* Article cover additionally to Article image, the first is more like a
  thumbnail, the second one for larger picture;
* Article pinning;
* Lead text for Category;
* Private article (for authenticated users only);
* Optional breadcrumbs;

On hold features:

* Move CKEditor usage in a contrib package (and let possibilities to use another
  editor like Summernote);
* Django-CMS plugin in a contrib package;
* A way to implement again Article modularity;
