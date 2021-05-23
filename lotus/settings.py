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
