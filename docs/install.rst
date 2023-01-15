.. _intro_install:

=======
Install
=======

Install package with every extra features in your environment : ::

    pip install django-blog-lotus[breadcrumbs]

Or without any features: ::

    pip install django-blog-lotus

For development install see :ref:`install_development`.


Configuration from scratch
**************************

Add it to your installed Django apps in settings : ::

    INSTALLED_APPS = (
        ...
        "view_breadcrumbs",
        "lotus.apps.LotusConfig",
    )

Remove the line with ``view_breadcrumbs`` if you didn't installed the full features.

Then load default application settings in your settings file: ::

    from lotus.settings import *

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

And finally your project needs a ``skeleton.html`` template like this: ::

    {% load i18n view_breadcrumbs lotus %}{% get_current_language as LANGUAGE_CODE %}<!DOCTYPE html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block head_title %}{% trans "Lotus weblog" %}{% endblock head_title %}</title>
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

Only the ``content block`` is required and the ``breadcrumbs`` one also if you
installed Lotus with breadcrumb extra requirement.

Once finished, you can run the Django command to apply the Lotus migrations. Also, you
will need to create a superuser or an admin to write contents from Django admin.


.. _intro_install_settings:

Settings
********

.. automodule:: lotus.settings
   :members:

.. _intro_install_demo:

Demonstration
*************

You may also install the full demonstration which implement all the feature in a ready
to start Django project. This requires Git, pip, virtualenv and make tools. Copy this
repository where you want, enter in repository directory and use the Makefile task: ::

    make install

This installs everything to run and develop. When done you may first create a
superuser: ::

    make superuser

And finally automatically fill some demonstration Author, Article and Category
objects: ::

    make demo

Careful, the ``demo`` command has hardcoded argument values for enabled languages to
match the ones from sandbox settings. You need to adjust these command arguments to fit
to your language settings from ``settings.LANGUAGES``.
