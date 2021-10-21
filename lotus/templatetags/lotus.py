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

    Usage: ::

        {% load lotus %}
        {% article_state_list article [now=custom_now] [prefix="foo_"] %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included.
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

    Usage: ::

        {% load lotus %}
        {% article_states article [now=custom_now] [prefix="foo_"] %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included.
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
def translation_siblings(context, source, **kwargs):
    """
    A tag to get translation siblings for given source object.

    This tag can work for an Article or a Category object to retrieve every translation
    siblings, like all translation children for an original source or translation
    children and original for a translation.

    Note than for an Article the tag will require a datetime it may refer to for
    filtering results with publication criterias. Either the datetime is set as a
    template context variable ``lotus_now`` as implemented in ``ArticleFilterMixin`` or
    it can be given through the tag argument ``now``.

    Usage: ::

        {% load lotus %}
        {% translation_siblings article [now=custom_now] [template="foo/bar.html"] %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included. This is only used
            with an Article object, so it should be safe to be empty for a Category.
        source (object): Either a ``lotus.models.Article`` or ``lotus.models.Category``
            to retrieve its translation siblings.

    Keywords Arguments:
        now (datetime.datetime): A datetime to use to compare against publish
            start and end dates to check for some publication criterias. Only used
            for Article object.
        template (string): A path to a custom template to use instead of the default
            one. If not given, the default one will be used, each model have its own
            default template, see settings.

    Returns:
        string: Rendered template tag fragment.

    """
    model = type(source)

    # Use the right template depending model
    if isinstance(source, Article):
        template_path = (
            kwargs.get("template") or settings.LOTUS_ARTICLE_SIBLING_TEMPLATE
        )
    elif isinstance(source, Category):
        template_path = (
            kwargs.get("template") or settings.LOTUS_CATEGORY_SIBLING_TEMPLATE
        )
    # If unsupported model has been given
    else:
        raise TemplateSyntaxError(
            "'translation_siblings' only accepts a Category or Article object for "
            "'source' argument."
        )

    # Get the base queryset for siblings
    siblings = model.objects.get_siblings(source=source)

    # Article model make additional filtering on publication criteria if not in admin
    # mode
    if (
        isinstance(source, Article) and
        not context.get(AdminModeMixin.adminmode_context_name, False)
    ):
        lotus_now = kwargs.get("now") or context.get("lotus_now")
        if lotus_now is None:
            raise TemplateSyntaxError(
                "'translation_siblings' require either a context variable 'lotus_now' "
                "to be set or a tag argument named 'now'."
            )

        siblings = siblings.get_published(target_date=lotus_now)

    return loader.get_template(template_path).render({
        "source": source,
        "siblings": siblings.order_by("language"),
    })
