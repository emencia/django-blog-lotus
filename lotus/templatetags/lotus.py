from django.conf import settings
from django.template import TemplateSyntaxError, Library, loader

from ..models import Article, Category
from ..views import AdminModeMixin

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
def translation_siblings(context, source, tag_name=None, **kwargs):
    """
    A tag to get translation siblings for given source object.

    This tag can work for an Article or a Category object to retrieve every translation
    siblings, like all translation children for an original source or translation
    children and original for a translation.

    Note than for Article object the tag will require a datetime it may refer to for
    filtering results with publication criterias. Either the datetime will be set as a
    template context variable ``lotus_now`` (as implemented in ``ArticleFilterMixin``)
    or it can be given through the tag argument ``now``.

    Usage: ::

        {% load lotus %}
        {% translation_siblings_html article [now=custom_now] [admin_mode=True|False] %}

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
        admin_mode (boolean): Option to bypass checking admin mode from context and
            force it to a value, either True to enable it, False to disable it or None
            to let the basic behavior to determine it from its template context
            variable. Default to None.
        tag_name (string): Template tag name to display in error messages. This is
            something used in template tags which inherit from ``translation_siblings``.
            You don't have to care about it in your common template tag usage.

    Returns:
        dict: A dictionnary with item ``source`` for the given source object and item
            ``siblings`` for retrieved translation sibling objects.

    """
    model = type(source)

    tag_name = tag_name or "translation_siblings"

    admin_mode = context.get(AdminModeMixin.adminmode_context_name, False)
    if kwargs.get("admin_mode", None) is not None:
        admin_mode = kwargs.get("admin_mode")

    # If unsupported model has been given
    if not isinstance(source, Article) and not isinstance(source, Category):
        source_name = type(source).__name__
        raise TemplateSyntaxError(
            (
                "'{tag_name}' only accepts a Category or Article object "
                "for 'source' argument. Object type '{source_name}' was given."
            ).format(tag_name=tag_name, source_name=source_name)
        )

    # Get the base queryset for siblings
    siblings = model.objects.get_siblings(source=source)

    # Article model make additional filtering on publication criteria if not in admin
    # mode
    if isinstance(source, Article) and not admin_mode:
        lotus_now = kwargs.get("now") or context.get("lotus_now")
        if lotus_now is None:
            raise TemplateSyntaxError(
                (
                    "'{tag_name}' require either a context variable 'lotus_now' to be "
                    "set or a tag argument named 'now'."
                ).format(tag_name=tag_name)
            )

        siblings = siblings.get_published(target_date=lotus_now)

    # Enforce order on language code
    siblings = siblings.order_by("language")

    # All available language names and codes
    existing_languages = [item.language for item in [source] + list(siblings)]
    available_languages = [
        code
        for code, name in settings.LANGUAGES
        if (code not in existing_languages)
    ]

    return {
        "source": source,
        "siblings": siblings,
        "existing_languages": existing_languages,
        "available_languages": available_languages,
    }


@register.simple_tag(takes_context=True)
def translation_siblings_html(context, source, **kwargs):
    """
    Work like ``translation_siblings`` but render HTML from a template instead.

    Usage: ::

        {% load lotus %}
        {% translation_siblings_html article [now=custom_now] [template="foo/bar.html"] [admin_mode=True|False] %}

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
        admin_mode (boolean): Option to bypass checking admin mode from context and
            force it to a value, either True to enable it, False to disable it or None
            to let the basic behavior to determine it from its template context
            variable. Default to None.

    Returns:
        string: Rendered template tag fragment.

    """  # noqa: E501
    # Use the right template depending model
    if isinstance(source, Article):
        template_path = (
            kwargs.get("template") or settings.LOTUS_ARTICLE_SIBLING_TEMPLATE
        )
    elif isinstance(source, Category):
        template_path = (
            kwargs.get("template") or settings.LOTUS_CATEGORY_SIBLING_TEMPLATE
        )

    render_context = translation_siblings(
        context,
        source,
        tag_name="translation_siblings_html",
        **kwargs
    )

    return loader.get_template(template_path).render(render_context)
