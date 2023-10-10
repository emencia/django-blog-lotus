.. _django-smart-media: https://github.com/sveetch/django-smart-media
.. _django-view-breadcrumbs: https://github.com/tj-django/django-view-breadcrumbs
.. _django-taggit: https://github.com/jazzband/django-taggit

.. _languages_intro:

==================================================
Internationalization, localization and translation
==================================================

Lotus include everything to make a weblog in many languages.


Internationalization
********************

**Language is selected from URL request** with a prefix like ``/fr/`` and user can
choose to browse in another one using the language menu.

This **menu will switches user to the language** index page. On default when user has no
session yet and come on site without the language prefix, its **language is guessed
from its browser** and fallback on the default site one.

Available languages are defined from
`Django settings <https://docs.djangoproject.com/en/4.1/ref/settings/#languages>`_.

.. Note::

    If you remove an available language from your settings all object related to
    removed language will remain untouched in your database, however they won't be
    reachable anymore from your site frontend.


Localization
************

All frontend interface textes can be translated through
`Django localization <https://docs.djangoproject.com/en/4.1/topics/i18n/translation/#how-to-create-language-files>`_
with message files (``*.po`` files) but Lotus only support english and french for now.


Content translation
*******************

**Category** and **Article** objects can be translated to an available language.

Lotus does not store translation on the same object. Instead **a new object is created
for each language** then related to the original one.

An object is considered as an original if it does not have any relation to another
"original" object. An object with a relation to another original is considered as a
"translation".

.. Note::

    * An object can only relate to a single original object;
    * You can't create a translation in the same language than the original one;
    * You can't create a translation with the same language twice;

    You can change article language and original relation at any time but it will be
    validated against these rules.

Since translation objects are complete new objects, you can change every content from
a language version to another.

Finally **Lotus never mixes and list objects from different languages**, only objects
for the user selected language. With the "original" and "translation" conception, an
user can go to another object language version since they are listed in object detail
page. Also this concept allow you to have object dedicated to a single specific
language.

Concretely as it can be seen from Article admin, objects will list to this tree: ::

    .
    ├── cheese
    ├── bread
    ├── fromage
    ├── pain
    └── omelette

But browsing objects would resolve to this sitemap tree: ::

    .
    ├── en
    │   ├── cheese
    │   └── bread
    └── fr
        ├── fromage
        ├── pain
        └── omelette

So a french user would see this Article list: ::

    ├── fromage
    ├── pain
    └── omelette

And see the english article tree if it switches to this language.
