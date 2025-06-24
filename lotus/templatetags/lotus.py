from django.conf import settings
from django.template import Library, TemplateSyntaxError, loader

from ..models import Album, Article, Category
from ..utils.language import get_language_code

register = Library()


@register.simple_tag(takes_context=True)
def article_state_list(context, article, **kwargs):
    """
    Return all state names for given article object.

    This is a shortcut around ``Article.get_states`` to be able to use the ``lotus_now``
    context variable or force another value.

    Exemple:
        At least you must give an Article object: ::

            {% load lotus %}
            {% article_state_list article [now=custom_now] [prefix="foo_"] %}

        * Optional ``now`` argument expect a datetime to use instead of current date;
        * Optional ``prefix`` argument expect a string to prepend all returned state
          names.

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included.
        article (lotus.models.article.Article): Article object to compute states.

    Keyword Arguments:
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

    Exemple:
        At least you must give an Article object: ::

            {% load lotus %}
            {% article_states article [now=custom_now] [prefix="foo_"] %}

        * Optional ``now`` argument expect a datetime to use instead of current date;
        * Optional ``prefix`` argument expect a string to prepend all returned state
          names.

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included.
        article (lotus.models.article.Article): Article object to compute states.

    Keyword Arguments:
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

    Exemple:
        At least you must give an Article object: ::

            {% load lotus %}
            {% translation_siblings_html article [now=custom_now] [preview=True] %}

        * Optional ``now`` argument expect a datetime to use instead of current date;
        * Optional ``preview`` argument expect a boolean to explicitely disable or
          enable preview mode, on default it is ``None`` to determine it automatically.

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included. This is only used
            with an Article object, so it should be safe to be empty for a Category.
        source (object): Either a ``lotus.models.Article`` or ``lotus.models.Category``
            to retrieve its translation siblings.

    Keyword Arguments:
        now (datetime.datetime): A datetime to use to compare against publish
            start and end dates to check for some publication criterias. Only used
            for Article object.
        preview (boolean): Option to bypass checking preview mode from context and
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

    preview = context.get(settings.LOTUS_PREVIEW_VARNAME, False)
    if kwargs.get("preview", None) is not None:
        preview = kwargs.get("preview")

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
    if isinstance(source, Article) and not preview:
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

    Exemple:
        At least you must give an Article object: ::

            {% load lotus %}
            {% translation_siblings_html article [now=custom_now] [template="foo/bar.html"] [preview=True] %}

        * Optional ``now`` argument expect a datetime to use instead of current date;
        * Optional ``template`` argument expect a string for a template path to use
          instead of default one;
        * Optional ``preview`` argument expect a boolean to explicitely disable or
          enable preview mode, on default it is ``None`` to determine it automatically;

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included. This is only used
            with an Article object, so it should be safe to be empty for a Category.
        source (object): Either a ``lotus.models.Article`` or ``lotus.models.Category``
            to retrieve its translation siblings.

    Keyword Arguments:
        now (datetime.datetime): A datetime to use to compare against publish
            start and end dates to check for some publication criterias. Only used
            for Article object.
        template (string): A path to a custom template to use instead of the default
            one. If not given, the default one will be used, each model have its own
            default template, see settings.
        preview (boolean): Option to bypass checking preview mode from context and
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


@register.inclusion_tag(settings.LOTUS_PREVIEW_SWITCH_TEMPLATE, takes_context=True)
def preview_switch(context):
    """
    Display a button to enable or disable preview mode.

    Render templates is defined from setting ``LOTUS_PREVIEW_SWITCH_TEMPLATE``.

    Exemple:
        This tag does not expect any argument: ::

            {% load lotus %}
            {% preview_switch %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included. Note that context
            requires the session and user objects to be present (when available for
            authenticated users) so you need to enable the respective middleware/context
            processors in your project settings.

    Returns:
        dict: A dictionnary of payload to build preview button template.

        * user: User object (or Anonymous)
        * allowed: Boolean to determine if user is allowed for preview mode or not;
        * current_mode: Either ``enabled`` or ``disabled`` string to indicate current
          preview mode state;
        * redirection: A string for the path to give to button URL that will be used
          to redirect to once preview toggle has been requested;
    """
    allowed = False
    current_mode = None
    redirection = None

    request = context.get("request")
    session = getattr(request, "session", None)
    user = getattr(request, "user", None)

    if user and user.is_staff:
        allowed = True
        redirection = request.get_full_path()
        current_mode = "disabled"

        if session.get(settings.LOTUS_PREVIEW_KEYWORD, None) is True:
            current_mode = "enabled"

    return {
        "user": user,
        "allowed": allowed,
        "current_mode": current_mode,
        "redirection": redirection,
    }


@register.simple_tag(takes_context=True)
def check_object_lang_availability(context, source, **kwargs):
    """
    Determine if an object has a language that are not available from ``LANGUAGES``
    setting.

    Exemple:
        This tag does not expect any other argument than ``source``: ::

            {% load lotus %}
            {% check_object_lang_availability article_object as object_lang_availability %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variables. It is not used from this tag.
        source (object): Any object with an attribute ``language`` that will be checked
            against ``settings.LANGUAGES`` however the tag will fails silently for
            given source that does not have this attribute.

    Returns:
        dict: A dictionnary with summary informations of object language and its
        availability.
    """  # noqa: E501
    is_available = False

    if getattr(source, "language", None):
        is_available = source.language in [k for k, v in settings.LANGUAGES]

    return {
        "is_available": is_available,
        "languages": settings.LANGUAGES,
        "language_keys": [k for k, v in settings.LANGUAGES],
        "language_labels": [v for k, v in settings.LANGUAGES],
    }


@register.simple_tag(takes_context=True)
def article_get_related(context, article, **kwargs):
    """
    Returns the related articles for a given article object.

    It rely on an optional filtering function used to filter article objects to apply
    publication and language lookups. This function is searched in template context
    as an item named ``apply_article_lookups``, if not found no filtering is applied.

    Commonly the filtering function would be
    ``ArticleFilterMixin.apply_article_lookups`` that is already supplied in Article
    detail view and viewset.

    Exemple:
        You must give an Article object: ::

            {% load lotus %}
            {% article_get_related myarticle %}

        Or:

            {% load lotus %}
            {% article_get_related myarticle as relateds %}

        No other arguments are expected.

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included.
        article (lotus.models.article.Article): Article object to compute states.

    Returns:
        queyrset: Queryset for retrieved related articles.
    """
    filter_func = context.get("article_filter_func", None)

    return article.get_related(filter_func=filter_func)


@register.simple_tag(takes_context=True)
def get_categories(context, current=None):
    """
    Generates and returns a flat list of all categories for current language.

    .. Note::
        This does not care about category tree, everything is returned in a flat list.
        See instead ``get_category_tree_html`` for a tree.

    Exemple:
        This tag does not require any argument to work: ::

            {% load lotus %}
            {% get_categories_html [current=mycategory] %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included.

    Keyword Arguments:
        current (lotus.models.article.Category): A category object to use in template
            to find the current category in the tree so it can marked as an active item.

    Returns:
        dict: A dictionary containing a list of dictionaries, each of which has the
        ``title`` and ``url`` of a category.
    """
    request = context.get("request", None)
    queryset = Category.objects.get_for_lang(get_language_code(request=request))

    if current and not isinstance(current, Category):
        current_type = type(current).__name__
        raise TemplateSyntaxError(
            (
                "'get_categories' tag only accepts a Category object as 'current' "
                "argument. Object type '{current_type}' was given."
            ).format(current_type=current_type)
        )

    return {
        "categories": [
            {
                "title": category.title,
                "url": category.get_absolute_url(),
                "is_active": (category.id == current.id) if current else False
            }
            for category in queryset.order_by(*Category.COMMON_ORDER_BY)
        ]
    }


@register.simple_tag(takes_context=True)
def get_categories_html(context, current=None, template=None):
    """
    Work like ``get_categories`` but render HTML from a template instead.

    Exemple:
        This tag does not require any argument to work: ::

            {% load lotus %}
            {% get_categories_html [current=mycategory] [template="foo/bar.html"] %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included. This is only used
            with an Article object, so it should be safe to be empty for a Category.

    Keyword Arguments:
        current (lotus.models.article.Category): A category object to use in template
            to find the current category in the tree so it can marked as an active item.
        template (string): A path for custom template to use. If not given a default
            one will be used from setting ``LOTUS_CATEGORIES_TAG_TEMPLATE``.

    Returns:
        string: Rendered template tag fragment.

    """  # noqa: E501
    # Use given template if any else the default one from settings
    template_path = template or settings.LOTUS_CATEGORIES_TAG_TEMPLATE

    render_context = get_categories(
        context,
        current=current,
    )

    return loader.get_template(template_path).render(render_context)


@register.simple_tag(takes_context=True)
def get_category_tree_html(context, parent=None, current=None, branch=None,
                           template=None):
    """
    Build HTML of a category tree for current language.

    The returned tree is not a queryset, it is a recursive list where each node is in
    the following form: ::

        {
            "data": {
                "language": "en",
                "original": None,
                "modified": now,
                "title": "Item 1",
                "slug": "item-1",
                "lead": "",
                "description": "",
                "cover": "",
            },
            "id": 1,
            "active": False,
            "depth": 1,
            "path": "0001",
            "children": []
        }

    The ``children`` is in fact only present in payload if the node has children.

    Exemple:
        This tag does not require any argument to work: ::

            {% load lotus %}
            {% get_category_tree_html [parent=mycategory] [current=anothercategory] [branch=True] [template="foo/bar.html"] %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included. This is only used
            with an Article object, so it should be safe to be empty for a Category.

    Keyword Arguments:
        parent (Category): A category object used to start the tree. If not given,
            we assume than parent is the root of all categories meaning the whole
            tree will be listed.
        current (Category): Basically the current category is only used to mark a
            node as "active". But with ``branch`` argument enabled it will be used
            for the "branch unfolding" mode.
        branch (boolean): The current category will be used to find the tree branch
            to unfold. When this is true and ``current`` is given, only the nodes
            from the tree branch will be unfolded along the top level nodes (with
            the same depth than the parent).
        template (string): A path for custom template to use. If not given a default
            one will be used from setting ``LOTUS_CATEGORY_TREE_TAG_TEMPLATE``.

    Returns:
        string: Rendered template tag fragment.

    """  # noqa: E501
    # Use given template if any else the default one from settings
    template_path = template or settings.LOTUS_CATEGORY_TREE_TAG_TEMPLATE

    request = context.get("request", None)
    language = get_language_code(request=request)
    branch = branch if branch else False

    return loader.get_template(template_path).render({
        "nodes": Category.get_nested_tree(
            language=language,
            parent=parent,
            current=current,
            branch=branch,
        ),
        "parent": parent,
        "current": current,
        "root_node": True,
    })


@register.simple_tag(takes_context=True)
def get_album_html(context, album, template=None):
    """
    Render an Album object with a template.

    Exemple:
        This tag requires ``album`` argument to work: ::

            {% load lotus %}
            {% get_album_html album %}

    Arguments:
        context (object): Either a ``django.template.Context`` or a dictionnary for
            context variable for template where the tag is included.
        album (lotus.models.article.Album): An album object.

    Keyword Arguments:
        template (string): A path for custom template to use. If not given a default
            one will be used from setting ``LOTUS_ALBUM_TAG_TEMPLATE``.

    Returns:
        string: Rendered template tag fragment.
    """
    if album and not isinstance(album, Album):
        current_type = type(album).__name__
        raise TemplateSyntaxError(
            (
                "'get_album_html' tag only accepts an Album object as 'album' "
                "argument. Object type '{current_type}' was given."
            ).format(current_type=current_type)
        )
    # Use given template if any else the default one from settings
    template_path = template or settings.LOTUS_ALBUM_TAG_TEMPLATE

    return loader.get_template(template_path).render({
        "album_object": album,
    })
