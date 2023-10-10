.. _django-smart-media: https://github.com/sveetch/django-smart-media
.. _django-view-breadcrumbs: https://github.com/tj-django/django-view-breadcrumbs
.. _django-taggit: https://github.com/jazzband/django-taggit

.. _publication_intro:

====================================
Publication criterias and visibility
====================================

There are many parameters involved to show an Article in listing or detail views.

All of these parameters make a combination of criterias where a single one can prevent
to display an article.

The article language
    It is not considered as a publication criteria but will avoid to list articles in
    another language than the user selected one.

The publication status
    By default an article is a "draft" but admin writer can choose to pass it as
    "available" and vice versa as much as it wants.

    A draft article is not reachable from lambda users, but admins can view them in
    Django admin or in frontend with the "Preview mode".

The publication dates
    An article got publication start and end dates. The start date is used against the
    current date time to determine when the article can be displayed and the optional
    end date to determine when it will be hidden forever.

    An article without the optional end date will be showed forever.

States
    Additionally article can select multiple visibility states.

    * **Pinned**: The article is always displayed at the very top of article list even
      before other non pinned articles with a more recent start date. However pinned
      articles adopt the start date ordering between them;
    * **Private**: A private article is only displayed to any logged in users;
    * **Favorite**: This does not affect the visibility but can be used in custom layout
      to visually mark this article or used in some code to get them apart;

.. Note::

    Commonly, all querysets from views that use Article relation are subject to
    criterias. For example, a Category detail view won't show private or draft articles
    to an anonymous user.
