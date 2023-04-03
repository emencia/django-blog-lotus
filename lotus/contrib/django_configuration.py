from ..settings import (
    LOTUS_CATEGORY_PAGINATION,
    LOTUS_ARTICLE_PAGINATION,
    LOTUS_AUTHOR_PAGINATION,
    LOTUS_TAG_PAGINATION,
    LOTUS_ENABLE_TAG_INDEX_VIEW,
    LOTUS_ARTICLE_PUBLICATION_STATE_NAMES,
    LOTUS_ARTICLE_SIBLING_TEMPLATE,
    LOTUS_CATEGORY_SIBLING_TEMPLATE,
    LOTUS_PREVIEW_KEYWORD,
    LOTUS_PREVIEW_VARNAME,
    LOTUS_PREVIEW_SWITCH_TEMPLATE,
)

class LotusDefaultSettings:
    """
    Default Lotus settings class to use with a "django-configuration" class.

    Example:

        You could use it like so: ::

            from configurations import Configuration
            from lotus.contrib.django_configuration import LotusDefaultSettings

            class Dev(LotusDefaultSettings, Configuration):
                DEBUG = True

                LOTUS_CATEGORY_PAGINATION = 142

        This will override only the setting ``LOTUS_CATEGORY_PAGINATION``, all other
        Lotus settings will have the default values from ``lotus.settings``.
    """

    LOTUS_CATEGORY_PAGINATION = LOTUS_CATEGORY_PAGINATION

    LOTUS_ARTICLE_PAGINATION = LOTUS_ARTICLE_PAGINATION

    LOTUS_AUTHOR_PAGINATION = LOTUS_AUTHOR_PAGINATION

    LOTUS_TAG_PAGINATION = LOTUS_TAG_PAGINATION

    LOTUS_ENABLE_TAG_INDEX_VIEW = LOTUS_ENABLE_TAG_INDEX_VIEW

    LOTUS_ARTICLE_PUBLICATION_STATE_NAMES = LOTUS_ARTICLE_PUBLICATION_STATE_NAMES

    LOTUS_ARTICLE_SIBLING_TEMPLATE = LOTUS_ARTICLE_SIBLING_TEMPLATE

    LOTUS_CATEGORY_SIBLING_TEMPLATE = LOTUS_CATEGORY_SIBLING_TEMPLATE

    LOTUS_PREVIEW_KEYWORD = LOTUS_PREVIEW_KEYWORD

    LOTUS_PREVIEW_VARNAME = LOTUS_PREVIEW_VARNAME

    LOTUS_PREVIEW_SWITCH_TEMPLATE = LOTUS_PREVIEW_SWITCH_TEMPLATE