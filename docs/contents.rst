.. _django-smart-media: https://github.com/sveetch/django-smart-media
.. _django-view-breadcrumbs: https://github.com/tj-django/django-view-breadcrumbs
.. _django-taggit: https://github.com/jazzband/django-taggit

.. _contents_intro:

========
Contents
========

Lotus is a simple weblog engine that focus on proper content. There is multiple content
kinds:

Article
*******

The most important document kind. **An article have many content types** and relate
to authors, categories, tags and other articles with the same language.

In addition to **publication dates**, an article have many **state kinds** which
**influence its visibility** and may be used to change its look in layout
integration.


Author
******

This is a simple **proxy object to Django user object**. They are assigned to
articles as a simple references. Author does not have any additional contents to a
Django user.


Category
********

A category is just a **container to organize your main article thematics**. It has
a title, a cover and a free description.

A category detail will list its related articles.


Tag
***

This is **alike Category but serve another content structure purposes**. They are
managed with `django-taggit`_ and does not have any other content than a name and a
slug.

These tags can be shared with another applications using `django-taggit`_ but Lotus
views are made to only show tag related to articles.

A tag detail will list its related articles. Tags are not subject to translation or
language, a same tag can be shared throught differents languages.

.. Warning::

    The tag slug ``autocomplete`` should be forbidden to create since this word
    is used in some urls, therefore the Tag detail page would never be reachable.
