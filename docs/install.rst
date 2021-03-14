.. _intro_install:

=======
Install
=======

Install package in your environment : ::

    pip install django-blog-lotus

For development usage see :ref:`install_development`.

Configuration
*************

Add it to your installed Django apps in settings : ::

    INSTALLED_APPS = (
        ...
        'lotus',
    )

Then load default application settings in your settings file: ::

    from lotus.settings import *

And finally apply database migrations.

Settings
********

.. automodule:: lotus.settings
   :members:
