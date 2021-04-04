.. _Python: https://www.python.org/
.. _Django: https://www.djangoproject.com/

=================
Django Blog Lotus
=================

A weblog application with Django.

This is a currently an ongoing work, don't expect anything ready for any usage.

Dependancies
************

* `Python`_>=3.6;
* `Django`_>=3.1;

Links
*****

* (Not yet) Read the documentation on `Read the docs <https://django-blog-lotus.readthedocs.io/>`_;
* (Not yet) Download its `PyPi package <https://pypi.python.org/pypi/django-blog-lotus>`_;
* Clone it on its `Github repository <https://github.com/emencia/django-blog-lotus>`_;

Differences with Zinnia
***********************

Some of Zinnia features have been dropped:

* Category have no more "tree" levels feature;
* All feature related to "discussion" (pingback, comments, etc..);
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

Planned features:

* Rest API;
