from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_article_states(context, article, **kwargs):
    """
    Return a string of all article state names

    Keywords Arguments:
        now (datetime.datetime): A datetime to use to compare against publish
            start and end dates to check for some publication criterias. See
            ``Article.get_states`` docstring for more details.
        prefix (string): A string to prefix every names. Empty by default.

    Returns:
        string: A string of every state names divided by a white space.
    """
    now = kwargs.get("now") or context.get("lotus_now")
    prefix = kwargs.get("prefix")

    return article.get_states(now=now)
