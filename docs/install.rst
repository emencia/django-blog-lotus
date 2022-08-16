.. _intro_install:

=======
Install
=======

Install package with every features in your environment : ::

    pip install django-blog-lotus[breadcrumbs]

Or without any features: ::

    pip install django-blog-lotus

For development install see :ref:`install_development`.


Configuration
*************

Add it to your installed Django apps in settings : ::

    INSTALLED_APPS = (
        ...
        "view_breadcrumbs",
        "lotus.apps.LotusConfig",
    )

Remove the line with ``view_breadcrumbs`` if you didn't installed the full features.

Then load default application settings in your settings file: ::

    from lotus.settings import *

And finally apply database migrations.


Settings
********

.. automodule:: lotus.settings
   :members:

Demonstration
*************

You may also install the full demonstration which implement all the feature in ready
to start Django project. This requires Git, pip, virtualenv and make tools. Copy this
repository where you want, enter in repository directory and just the Makefile: ::

    make install

This installs everything to run and develop. When done, you may create a first
superuser: ::

    make superuser

And finally automatically fill some demonstration Author, Article and Category
objects: ::

    make lotus_demo

Careful, the ``lotus_demo`` has hardcoded values for enabled translations to match
the ones from settings, it won't work if you previously edited settings to change
available languages from ``settings.LANGUAGES``.
