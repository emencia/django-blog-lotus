"""
Test utilities
"""
from django.test.html import parse_html
from django.template.response import TemplateResponse

from pyquery import PyQuery as pq


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
