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

LOTUS_TRANSLATE_CONTENT = True
"""
Determine if your project enable content translation or not.

TODO: Not used yet, lotus is always in translated mode.
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
``available`` state, never for ``draft``.

In practice ``draft``, ``publish_start_below`` and ``publish_end_passed`` states will
only be visible for admin in preview mode.

``private`` state will only be visible to authenticated users.
"""
