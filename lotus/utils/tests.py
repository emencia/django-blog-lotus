"""
==============
Test utilities
==============

"""
from django.contrib.sites.models import Site
from django.template.response import TemplateResponse
from django.test.html import parse_html
from django.urls import reverse

from pyquery import PyQuery as pq


# A dummy password that should pass form validation
VALID_PASSWORD_SAMPLE = "Azerty12345678"


def get_website_url(site_settings):
    """
    A shortand to retrieve the full website URL according to Site ID and HTTP
    protocole settings.

    Arguments:
        site_settings (django.conf.settings): Settings object.

    Returns:
        string: Full website URL.
    """
    domain = Site.objects.get_current().domain
    protocol = "https://" if site_settings.HTTPS_ENABLED else "http://"

    return "".join([protocol, domain])


def get_relative_path(site_url, url):
    """
    From given URL, retrieve the relative path (URL without domain and starting
    slash).

    Arguments:
        site_url (string): Website URL to remove from given ``url``
            argument.
        url (string): Full URL (starting with http/https) to make relative to
            website URL.

    Returns:
        string: Admin change view URL path for given model object.
    """
    if url.startswith(site_url):
        return url[len(site_url):]

    return url


def get_admin_add_url(model):
    """
    Return the right admin URL for add form view for given class.

    Arguments:
        model (Model object): A model object to use to find its admin
            add form view URL.

    Returns:
        string: Admin add form view URL path.
    """
    url_pattern = "admin:{app}_{model}_add"

    return reverse(url_pattern.format(
        app=model._meta.app_label,
        model=model._meta.model_name
    ))


def get_admin_change_url(obj):
    """
    Return the right admin URL for a change view for given object.

    Arguments:
        obj (Model object): A model object instance to use to find its admin
            change view URL.

    Returns:
        string: Admin change view URL path.
    """
    url_pattern = "admin:{app}_{model}_change"

    return reverse(url_pattern.format(
        app=obj._meta.app_label,
        model=obj._meta.model_name
    ), args=[
        obj.pk
    ])


def get_admin_list_url(model):
    """
    Return the right admin URL for a list view for given class.

    Arguments:
        model (Model object): A model object to use to find its admin
            list view URL.

    Returns:
        string: Admin list view URL path.
    """
    url_pattern = "admin:{app}_{model}_changelist"

    return reverse(url_pattern.format(
        app=model._meta.app_label,
        model=model._meta.model_name
    ))


def decode_response_or_string(content):
    """
    Shortand to get HTML string from either a TemplateResponse (as returned
    from Django test client) or a simple string so you can blindly give a
    response or a string without to care about content type.

    Arguments:
        content (TemplateResponse or string): If content is a string it will
            just return it. If content is a TemplateResponse it will decode byte
            string from its ``content`` attribute.

    Returns:
        string: HTML string.
    """
    if isinstance(content, TemplateResponse):
        return content.content.decode()
    return content


def html_element(content):
    """
    Shortand to use Django HTML parsing on given content.

    This is more useful for comparaison on HTML parts.

    Arguments:
        content (TemplateResponse or string): HTML content to parse.

    Returns:
        django.test.html.Element: A Python object structure able to perform
        comparaison on a semantical way. See ``django.test.html.parse_html`` for
        more details.
    """
    return parse_html(
        decode_response_or_string(content)
    )


def html_pyquery(content):
    """
    Shortand to use Pyquery parsing on given content.

    This is more useful to dig in advanced HTML content. PyQuery is basically a
    wrapper around ``lxml.etree`` it helps with a more intuitive API (alike
    Jquery) to traverse elements but when reaching a node content it will
    return ``lxml.html.HtmlElement`` object which have a less intuitive API.

    Arguments:
        content (TemplateResponse or string): HTML content to parse.

    Returns:
        pyquery.PyQuery: A PyQuery object.
    """
    return pq(
        decode_response_or_string(content),
        parser='html'
    )


def queryset_values(queryset, names=["slug", "language"],
                    orders=["slug", "language"]):
    """
    An helper to just return a list of dict values ordered from given queryset.

    Arguments:
        queryset (Queryset): A queryset to turn to values.

    Keyword Arguments:
        names (list): A list of field names to return as values for each object.
            Default return "slug" and "language" values only.
        orders (list): A list of field names to order results.
            Default order first on "slug" then "language".

    Returns:
        list: A list of dict items for all result objects.
    """
    return list(
        queryset.values(*names).order_by(*orders)
    )
