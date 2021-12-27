"""
Default application settings
----------------------------

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
only be visible for admin in preview mode, since other users can not view this kind
of articles.

In the same way the ``private`` state will only be visible to authenticated users.
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
