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
to authors, categories, tags, album and other articles with the same language.

In addition to **publication dates**, an article have many **state kinds** which
**influence its visibility** and may be used to change its look in layout
integration.


Author
******

This is a simple **proxy object to Django user object**. They are assigned to
articles as a simple references.

Author does not have any additional contents to a Django user.


Category
********

A category is just a **container to organize your main article thematics**.

Category has a title, a lead, a cover and a free optional description.

A category can define a parent category so it will be assumed as a child of the parent.

.. Warning::
    A category can not be a parent of another category with different languages, if
    you try to do so the admin form will raise an error.

* The category list view will only lists the first level categories;
* The category detail view will list its related articles and its possible children
  categories;


Tag
***

This is **alike Category but serve another content structure purpose**.

They are managed with `django-taggit`_ and does not have any other content than a name
and a slug.

These tags can be shared with another applications using `django-taggit`_ but Lotus
views are made to only show tag related to articles.

A tag detail will list its related articles. Tags are not subject to translation or
language, a same tag can be shared throught differents languages.

.. Warning::

    The tag slug ``autocomplete`` should be forbidden to create since this word
    is used in some urls, therefore the Tag detail page would never be reachable.


Album
*****

Album is a way to create a gallery of medias into an article.

Album itself only has a required title but it can holds many media items. An album
media item have an optional title, a number to set its order position and a media file.

Albums are managed outside of article objects to avoid performance issue with large
albums and ease their management. You create an album and then you can select it from
a single or many articles.

With translated articles, you are free select either the same albums for original
article and its translations or create a different album for original and translations.

.. Note::

    You can not share a same media item to many different albums since a media item is
    tied to a single album.