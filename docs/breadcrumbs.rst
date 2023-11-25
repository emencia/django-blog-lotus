.. _django-view-breadcrumbs: https://github.com/tj-django/django-view-breadcrumbs

.. _breadcrumbs_intro:

===========
Breadcrumbs
===========

Every page include breadcrumbs from starting site entry point (commonly the homepage)
to the current page if `django-view-breadcrumbs`_ has been installed as explained from
:ref:`intro_install` document, read the `django-view-breadcrumbs`_ documentation for
more informations on its available features and settings.

.. Note::
    View crumb titles can be changed from setting ``LOTUS_ENABLE_TAG_INDEX_VIEW``
    except those ones which use an object title as their crumb title like the detail
    views.

.. _install_breadcrumbs:

Install
*******

First you need to install Lotus with extra requirement for breadcrumbs: ::

    pip install django-blog-lotus[breadcrumbs]

Then enable it in Django enabled applications before the line for Lotus (in any order
with API): ::

    INSTALLED_APPS = (
        ...
        "view_breadcrumbs",
        ...
        "lotus",
    )

