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

LOTUS_TRANSLATE_CONTENT = True
"""
Determine if your project enable content translation or not.

TODO: Not used yet, lotus is always in translated mode.
"""

LOTUS_ARTICLE_PUBLICATION_STATE_NAMES = {
    "pinned": "article--pinned",
    "featured": "article--featured",
    "private": "article--private",
    "status_draft": "article--draft",
    "status_available": "article--available",
    "publish_start_below": "article--not-yet",
    "publish_end_passed": "article--passed",
}
"""
Available article state names.

You can remove an entry to ignore some states and they won't be returned in article
states.

Note than ``publish_start_below`` and ``publish_end_passed`` are only elligible with
``available`` state, never for ``draft``.

In practice ``draft``, ``publish_start_below`` and ``publish_end_passed`` states will
only be visible for admin in preview mode.

``private`` state will only be visible to authenticated users.
"""

LOTUS_ARTICLE_SIBLING_TEMPLATE = "lotus/article/partials/siblings.html"
"""
Default template to use for template tag ``get_article_languages``.
"""
