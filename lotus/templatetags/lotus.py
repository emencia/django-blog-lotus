"""
TODO:
    Template tags need better documentation strings with at least a sample usage.
"""
from django.conf import settings
from django.template import TemplateSyntaxError, Library, loader

from lotus.models import Article, Category
from lotus.views import AdminModeMixin

register = Library()


@register.simple_tag(takes_context=True)
def article_state_list(context, article, **kwargs):
    """
    Return all state names for given article object.

    This is a shortcut around ``Article.get_states`` to be able to use the ``lotus_now``
    context variable or force another value.

    Arguments:
        article (lotus.models.article.Article): Article object to compute states.

    Keywords Arguments:
        now (datetime.datetime): A datetime to use to compare against publish
            start and end dates to check for some publication criterias. See
            ``Article.get_states`` docstring for more details.
        prefix (string): A string to prefix every names. Empty by default.

    Returns:
        list: A list of every state names.
    """
    now = kwargs.get("now") or context.get("lotus_now")
    prefix = kwargs.get("prefix", "")

    states = [
        prefix + item
        for item in article.get_states(now=now)
    ]

    return states


@register.simple_tag(takes_context=True)
def article_states(context, article, **kwargs):
    """
    Return a string of state names for given article object.

    Identical to ``article_state_list`` but return a string instead of list.

    Arguments:
        article (lotus.models.article.Article): Article object to compute states.

    Keywords Arguments:
        now (datetime.datetime): A datetime to use to compare against publish
            start and end dates to check for some publication criterias. See
            ``Article.get_states`` docstring for more details.
        prefix (string): A string to prefix every names. Empty by default.

    Returns:
        string: Every state names divided by a white space.
    """
    now = kwargs.get("now") or context.get("lotus_now")
    prefix = kwargs.get("prefix", "")

    states = [
        prefix + item
        for item in article.get_states(now=now)
    ]

    return " ".join(states)


@register.simple_tag(takes_context=True)
def get_article_languages(context, source, **kwargs):
    """
    TODO:
    A tag to get source siblings (related original and translations).

    To work, this tag depends from template context variable ``lotus_now`` which is
    implemented from ``ArticleFilterMixin`` view mixin OR pass this date as keyword
    argument ``now`` to the tag.

    TODO:
    (Then do another one for category, no need of now/lotus_now)
    """
    template_path = kwargs.get("template") or settings.LOTUS_ARTICLE_SIBLING_TEMPLATE

    siblings = Article.objects.get_siblings(source=source)

    # If context variable for admin mode is not set or not True, the user are restricted
    # to view published siblings only
    if not context.get(AdminModeMixin.adminmode_context_name, False):
        lotus_now = kwargs.get("now") or context.get("lotus_now")
        if lotus_now is None:
            raise TemplateSyntaxError(
                "'get_article_languages' require either a context variable 'lotus_now' "
                "to be set or a tag argument named 'now'."
            )

        siblings = siblings.get_published(target_date=lotus_now)

    return loader.get_template(template_path).render({
        "source": source,
        "siblings": siblings.order_by("language"),
    })
