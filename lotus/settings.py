"""
.. _Django sitemap framework: https://docs.djangoproject.com/en/stable/ref/contrib/sitemaps/

These are the default settings you can override in your own project settings
right after the line which load the default app settings.
"""  # noqa
from django.utils.translation import gettext_lazy as _


LOTUS_CATEGORY_PAGINATION = 5
"""
Category per page limit for pagination, set it to ``None`` to disable
pagination.
"""

LOTUS_ARTICLE_PAGINATION = 10
"""
Article entry per page limit for pagination, set it to ``None`` to disable
pagination.
"""

LOTUS_AUTHOR_PAGINATION = 6
"""
Author per page limit for pagination, set it to ``None`` to disable
pagination.
"""

LOTUS_TAG_PAGINATION = 40
"""
Tag per page limit for pagination, set it to ``None`` to disable
pagination.
"""


LOTUS_ENABLE_TAG_INDEX_VIEW = True
"""
To allow (``True``) or not (``False``) the tag index view. This option exists because
tag index view may have performance issues and is not always required in some projects.

.. Note::

    The tag index part will still appears in breadcrumbs since it won't have any
    meaning to locate a tag detail at the root of Lotus breadcrumbs. However it won't
    have any link to click.

"""

LOTUS_ARTICLE_PUBLICATION_STATE_NAMES = {
    "pinned": "pinned",
    "featured": "featured",
    "private": "private",
    "status_draft": "draft",
    "status_available": "available",
    "publish_start_below": "not-yet",
    "publish_end_passed": "passed",
}
"""
Available article state names.

You can remove an entry to ignore some states and they won't be returned in article
states.

Note than ``publish_start_below`` and ``publish_end_passed`` are only elligible with
``available`` state enabled and never if ``draft`` state is enabled.

In practice ``draft``, ``publish_start_below`` and ``publish_end_passed`` states will
only be visible for admin in preview mode since other users can not view this kind
of articles.

In the same way the ``private`` state will only be visible to authenticated users.

You may change state value since they are mostly label however it can break some
default lotus templates which may use them so you will have to override these templates.
"""

LOTUS_ARTICLE_DETAIL_TEMPLATES = (
    ("lotus/article/detail.html", _("Default")),
)
"""
List of available template choices to render an Article object detail.
"""

LOTUS_CATEGORY_DETAIL_TEMPLATES = (
    ("lotus/category/detail.html", _("Default")),
)
"""
List of available template choices to render a Category object detail.
"""

LOTUS_ARTICLE_SIBLING_TEMPLATE = "lotus/article/partials/siblings.html"
"""
Default template used for template tag ``get_translation_siblings`` with an Article
object.
"""

LOTUS_CATEGORY_SIBLING_TEMPLATE = "lotus/category/partials/siblings.html"
"""
Default template used for template tag ``get_translation_siblings`` with an Category
object.
"""

LOTUS_PREVIEW_SWITCH_TEMPLATE = "lotus/preview_switch.html"
"""
Template path used to render template tag ``preview_switch``.
"""

LOTUS_CATEGORIES_TAG_TEMPLATE = "lotus/category/partials/tag_get_categories.html"
"""
Template path used to render template tag ``get_categories_html``.
"""

LOTUS_CATEGORY_TREE_TAG_TEMPLATE = "lotus/category/partials/tag_get_category_tree.html"
"""
Template path used to render template tag ``get_category_tree_html``.
"""

LOTUS_ALBUM_TAG_TEMPLATE = "lotus/album/partials/tag_get_album_html.html"
"""
Template path used to render template tag ``get_album_html``.
"""

LOTUS_PREVIEW_KEYWORD = "preview"
"""
Keyword name for preview mode in session
"""

LOTUS_PREVIEW_VARNAME = "preview_mode"
"""
Template context variable name to set the preview mode in views.
"""

LOTUS_CRUMBS_TITLES = {
    "article-index": _("Articles"),
    "author-index": _("Authors"),
    "category-index": _("Categories"),
    "tag-index": _("Tags"),
}
"""
Crumb title used for views breadcrumbs, for each item key uses the url name and value
is the title to display. You must not remove any of these, just change the value.

.. Note::

    Not all views have a static crumb title, like all detail views use directly the
    object title as a crumb title, so they won't be editable from this setting.

"""

LOTUS_CATEGORY_SHORT_CRUMBS = False
"""
Manage the length of category breadcrumbs. When false, all category ancestor are listed
in crumbs. When true, only the current category is listed in crumbs. This is only
applied on category children.
"""

LOTUS_ADMIN_ARTICLE_ASSETS = {
    "css": {
        "all": ("css/lotus-admin.css",)
    },
    "js": None,
}
"""
Form media to load in all admin views related to model Article. See Django
documentation about `admin form media definitions
<https://docs.djangoproject.com/en/stable/ref/contrib/admin/#modeladmin-asset-definitions>`_
to know how you can edit it.
"""  # noqa

LOTUS_ADMIN_CATEGORY_ASSETS = {
    "css": {
        "all": ("css/lotus-admin.css",)
    },
    "js": None,
}
"""
Form media to load in all admin views related to model Category. See Django
documentation about `admin form media definitions
<https://docs.djangoproject.com/en/stable/ref/contrib/admin/#modeladmin-asset-definitions>`_
to know how you can edit it.
"""  # noqa

LOTUS_ADMIN_ALBUM_ASSETS = {
    "css": {
        "all": ("css/lotus-admin.css",)
    },
    "js": None,
}
"""
Form media to load in all admin views related to model Album. See Django
documentation about `admin form media definitions
<https://docs.djangoproject.com/en/stable/ref/contrib/admin/#modeladmin-asset-definitions>`_
to know how you can edit it.
"""  # noqa

LOTUS_SITEMAP_AUTHOR_OPTIONS = {
    "changefreq": "monthly",
    "priority": 0.5,
}
"""
Author sitemap class options.

Supported `Django sitemap framework`_ options are:

* ``changefreq``;
* ``limit``;
* ``priority``;
* ``protocol``;

"""

LOTUS_SITEMAP_ARTICLE_OPTIONS = {
    "changefreq": "monthly",
    "priority": 0.51,
    "pinned_priority": 0.80,
    "featured_priority": 0.64,
}
"""
Article sitemap class options.

Supported `Django sitemap framework`_ options are:

* ``changefreq``;
* ``limit``;
* ``priority``;
* ``protocol``;

And additionnally the options:

* ``translations`` which expect a boolean value to enable (``True``) or disable
  (``False``) the :ref:`sitemaps_translation_mode`.
* ``pinned_priority`` the article get this priority if it has been pinned;
* ``featured_priority`` the article get this priority if it has been featured;

If article is pinned and featured, pinned state priority is used. Finally both states
overrides the default priority.
"""

LOTUS_SITEMAP_CATEGORY_OPTIONS = {
    "changefreq": "monthly",
    "priority": 0.5,
}
"""
Category sitemap class options.

Supported `Django sitemap framework`_ options are:

* ``changefreq``;
* ``limit``;
* ``priority``;
* ``protocol``;

And additionnally the option ``translations`` which except a boolean value to enable
or disable the :ref:`sitemaps_translation_mode`.
"""

LOTUS_SITEMAP_TAG_OPTIONS = {
    "changefreq": "monthly",
    "priority": 0.5,
}
"""
Tag sitemap class options.

Supported `Django sitemap framework`_ options are:

* ``changefreq``;
* ``limit``;
* ``priority``;
* ``protocol``;
"""

LOTUS_API_ALLOW_DETAIL_LANGUAGE_SAFE = True
"""
Allow API detail endpoint to ignore the language constraint. If setting is true,
detail endpoint won't add the language filter to the queryset to get an object. If
setting is false, the detail endpoint will enforce language on queryset.

Commonly you will let it set to true since API don't use ``i18n_url`` pattern and prefer
to know language choice from cookie or header that is not very handy when
navigating in the API browser. However in some case you may find this useful to enforce.

This behavior is applied for all translated models like Article and Category.

In any way, all other endpoints still filter on language especially for the lists that
need to not return mixed languages.
"""
