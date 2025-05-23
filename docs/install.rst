.. _django-smart-media: https://github.com/sveetch/django-smart-media
.. _Django REST framework: https://www.django-rest-framework.org/

.. _intro_install:

=======
Install
=======

Install package with every extra feature requirements in your environment : ::

    pip install django-blog-lotus[api,breadcrumbs]

Or without API and only breadcrumbs: ::

    pip install django-blog-lotus[breadcrumbs]

Or without any features: ::

    pip install django-blog-lotus

For development install see :ref:`install_development`.

.. _install_config_from_scratch:

Configuration from scratch
**************************

Enable required applications in your settings : ::

    INSTALLED_APPS = (
        "dal",
        "dal_select2",
        # Here the builtin django apps ...
        "treebeard",
        "sorl.thumbnail",
        "smart_media",
        "ckeditor",
        "ckeditor_uploader",
        "taggit",
        "lotus",
    )

.. Note::

    * The lines with ``dal`` and ``dal_select2`` always need to be before
      ``django.contrib.admin`` since it needs to be ready before admin;
    * There may be conflicts if your project use also the "easy-thumbnail"
      library. To avoid this you should put the lines with ``sorl.thumbnail`` and
      ``smart_media`` just after the Django builtin apps and always before
      "easy-thumbnail";

Then to properly enable multiple language you need to enable the middleware
``LocaleMiddleware`` (see Django documentation to now how to place it correctly): ::

    MIDDLEWARE = [
        ...
        "django.middleware.locale.LocaleMiddleware",
        ...
    ]

And then to enable some languages like so: ::

    LANGUAGE_CODE = "en"

    LANGUAGES = (
        ("en", "English"),
        ("fr", "Français"),
        ("de", "Deutsche"),
    )

Then load default applications settings in your settings file: ::

    from smart_media.settings import *
    from lotus.settings import *

.. Note::

    Instead, if your project use
    `django-configuration <https://django-configurations.readthedocs.io/en/stable/>`_,
    your settings class can inherits from
    ``lotus.contrib.django_configuration.LotusDefaultSettings`` (see it in
    :ref:`intro_references_contrib`) and the settings class from `django-smart-media`_.

Then add the required url parts in you project ``urls.py`` like this: ::

    from django.conf.urls.i18n import i18n_patterns
    from django.contrib import admin
    from django.urls import include, path


    urlpatterns = [
        path("admin/", admin.site.urls),
        path("ckeditor/", include("ckeditor_uploader.urls")),
        path("i18n/", include("django.conf.urls.i18n")),
    ]

    urlpatterns += i18n_patterns(
        path("", include("lotus.urls")),
    )

.. Note::
    This URL configuration mount Lotus URLs at root of your site, it may override other
    possible applications URLs. In this case you should mount Lotus under a specific
    path like: ::

        path("blog/", include("lotus.urls")),

    Now you will reach lotus from path ``/blog/``.


Optional features
-----------------

There is also some optional features that are not enabled on default, you may want
to enable them following their documentation:

* :ref:`api_intro`;
* :ref:`breadcrumbs_intro`;
* :ref:`sitemaps_intro`;


.. _install_single_language:

Single language site
--------------------

If you don't plan to use other languages, avoid the step about adding middleware
``LocaleMiddleware`` and only set the same language from settings ``LANGUAGE_CODE``
into ``LANGUAGES``: ::

    LANGUAGE_CODE = "en"

    LANGUAGES = (
        ("en", "English"),
    )


And finally don't mount Lotus urls with ``i18n_patterns``, just use: ::

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("ckeditor/", include("ckeditor_uploader.urls")),
        path("", include("lotus.urls")),
    ]


.. _install_integration:

Basic integration
-----------------

And finally your project needs a ``skeleton.html`` template like this: ::

    {% load i18n view_breadcrumbs lotus %}{% get_current_language as LANGUAGE_CODE %}<!DOCTYPE html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block header-title %}{% trans "Lotus weblog" %}{% endblock header-title %}</title>
        {% block metas %}{% endblock metas %}
    </head>

    <body>

    <div class="d-grid gap-3 p-3">
        <div class="main-content container-xxl">
            {% block breadcrumbs %}
                {% render_breadcrumbs "view_breadcrumbs/bootstrap5.html" %}
            {% endblock %}
            {% block content %}Sandbox skeleton{% endblock %}
        </div>
    </div>

    </body>
    </html>

Only the ``content`` block is required and the ``breadcrumbs`` one also if you
installed Lotus with breadcrumb extra requirement.

Once finished, you can run the Django command to apply the Lotus migrations. Also, you
will need to create a superuser or an admin to write contents from Django admin.

.. _install_demo:

Demonstration
*************

You may also install the full demonstration which implements all the features in a
Django project ready to start. This requires Git, pip, virtualenv, recent Node.js and
make tools. Clone this repository where you want, enter in repository directory and use
the Makefile tasks: ::

    make install frontend superuser

This installs everything to run and develop then build frontend assets and prompt you
to create a superuser.

And finally automatically fill some demonstration contents objects using command
``lotus_demo`` with default values: ::

    make demo

.. Note::

    The makefile command ``demo`` use hardcoded arguments values based on demonstration
    Lotus settings to enable languages for object creations.

    If you want to make a demonstration on some specific languages, you will need to
    edit your project setting ``settings.LANGUAGES`` and directly use the command
    ``lotus_demo`` to specify the right languages to use.

.. Warning::

    The ``lotus_demo`` command is currently not safe with various object lengths
    required from command arguments. Command has been done to work with default Lotus
    settings so the object length to create is based on pagination limits.

    In some case where you change an object length it may not cover the effectively
    required length from insertion. Indeed some object relation have uniqueness
    constraint which lead to consume random objects and may lead to empty remaining
    object queue.

    So this command may fails depending object lengths you required.
