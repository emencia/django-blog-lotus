from django.utils.translation import gettext_lazy as _

"""
These are the default settings you can override in your own project settings
right after the line which load the default app settings.
"""
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

LOTUS_ARTICLE_SIBLING_TEMPLATE = "lotus/article/partials/siblings.html"
"""
Default template to use for template tag ``get_translation_siblings`` with an Article
object.
"""

LOTUS_CATEGORY_SIBLING_TEMPLATE = "lotus/category/partials/siblings.html"
"""
Default template to use for template tag ``get_translation_siblings`` with an Category
object.
"""

LOTUS_PREVIEW_KEYWORD = "preview"
"""
Keyword name for preview mode in session
"""

LOTUS_PREVIEW_VARNAME = "preview_mode"
"""
Template context variable name to set the preview mode in views.
"""

LOTUS_PREVIEW_SWITCH_TEMPLATE = "lotus/preview_switch.html"
"""
Template path to use to render template tag ``preview_switch``.
"""

LOTUS_CRUMBS_TITLES = {
    "article-index": _("Articles"),
    "author-index": _("Authors"),
    "category-index": _("Categories"),
    "tag-index": _("Tags"),
}
"""
Crumb title to use for views breadcrumbs, for each item key uses the url name and value
is the title to display. You must not remove any of these, just change the value.

.. Note::

    Not all views have a static crumb title, like all detail views use directly the
    object title as a crumb title, so they won't be editable from this setting.

"""
