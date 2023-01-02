.. _intro_overview:

========
Overview
========

.. Note::

    This document is far from finished yet.

Writing
*******

An article has various text and media contents to write a proper actuality entry and
a category has some various content to organize your articles under thematics.

Basically you will start to create some main categories then write an article and
relate it to categories, authors and possibly to other articles.

An author is just a common user.

Media support
*************

TODO

* JPG
* PNG
* GIF
* SVG


Publishing
**********

TODO

* Draft
* Available


Marks
*****

* Pinned
* Favorite
* Private


Content translation
*******************

TODO


Breadcrumbs
***********

TODO


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
* Private article (for authenticated users only);
* Optional breadcrumbs;

On hold features:

* Move CKEditor usage in a contrib package (and let possibilities to use another
  editor like Summernote);
* Django-CMS plugin in a contrib package;
* A way to implement again Article modularity;
