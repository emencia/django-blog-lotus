"""
Default application settings
----------------------------

These are the default settings you can override in your own project settings
right after the line which load the default app settings.

TODO:
    * Prepend setting names with "LOTUS_"

"""
BLOG_PAGINATION = 5
"""
Blog entry per page limit for pagination, set it to ``None`` to disable
pagination.
"""

ARTICLE_PAGINATION = 6
"""
Article entry per page limit for pagination, set it to ``None`` to disable
pagination.
"""

TRANSLATE_CONTENT = True
"""
Determine if your project enable content translation or not.
"""
