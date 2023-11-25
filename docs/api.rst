.. _Django REST framework: https://www.django-rest-framework.org/

.. _api_intro:

===
API
===

Lotus has an optional Web API built with `Django REST framework`_ (also known as
**DRF**) and implements everything to get contents.

As said before, this is optional and you need to enable it on your own (see
below).

It currently have some difference with the HTML frontend:

* This is a read only API, you won't be able to use it to add, edit or delete contents;
* Preview mode is not implemented, meaning you won't be able to use to preview
  contents, you still need to continue to use the HTML frontend to do so;
* Not any images are thumbnailed, all media URLs point to the original uploaded file;


.. _install_api:

Install
*******

First you need to install Lotus with extra requirement for API: ::

    pip install django-blog-lotus[api]

Then you need to mount it in your urls, add the following line into the
``urlpatterns = [...]`` from project ``urls.py`` : ::

    path("api/", include("lotus.api_urls")),

Obviously you can use the url path you want instead of ``api/``.

Then enable it in Django enabled applications before Lotus (in any order with
Breadcrumbs): ::

    INSTALLED_APPS = (
        ...
        "rest_framework",
        ...
        "lotus",
    )

Also you may want to add settings for `Django REST framework`_ itself like these
ones: ::

    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": [
            # Use Django"s standard `django.contrib.auth` permissions,
            # or allow read-only access for unauthenticated users.
            "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
            # Only Django"s standard `django.contrib.auth` permissions, every
            # authenticated user can read and anonymous are never allowed
            # "rest_framework.permissions.DjangoModelPermissions",
        ],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
        "PAGE_SIZE": 20
    }


Internationalization
********************

Lotus API stands on what is implemented from
`DRF to determine language <https://www.django-rest-framework.org/topics/internationalization/#how-the-language-is-determined>`_.

On default installation, the API is not mounted with
``django.conf.urls.i18n.i18n_patterns`` so the only way to switch language is
through a cookie or HTTP headers. You can use ``i18n_patterns`` instead to allow for
language prefix in URL.


Authentication & Permissions
****************************

Default Lotus installation let the API usage to be opened to anyone. However from
your settings you may close it to authentificated user only : ::

    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": [
            # Only Django"s standard `django.contrib.auth` permissions, every
            # authenticated user can read and anonymous are never allowed
            "rest_framework.permissions.DjangoModelPermissions",
        ],
        ...
    }

Lotus on itself does not implement any specific permission.


Data serialization
******************

Lotus try a little bit to optimize request with specific serializer depending of
viewsets. This means that object list payload does not include every data from an
object, only the necessary fields.

So commonly for each model there are three serializers:

* The full one which output every fields from an object, it is means to be used for
  a detail viewset;
* The resumed one which outputs only necessary fields to list objects, it is means to
  be used for a list viewset;
* The minimal one which outputs only a few set of fields, it is means to be used when
  object is included into another object payload (like for Category into Article list);
