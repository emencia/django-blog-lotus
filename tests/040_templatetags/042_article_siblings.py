import datetime

import pytest
import pytz

from django.template import Context, Template, TemplateSyntaxError, TemplateDoesNotExist

from lotus.factories import multilingual_article, CategoryFactory
from lotus.utils.tests import html_pyquery
from lotus.views import AdminModeMixin


# Shortcuts for shorter variable names
ADMINMODE_CONTEXTVAR = AdminModeMixin.adminmode_context_name


def test_tag_get_article_languages_missing_now(db):
    """
    Tag "get_article_languages" requires an article object and context variable
    'lotus_now' or a tag argument 'now'.
    """
    ping = CategoryFactory(slug="ping")

    # Create cheese articles with published FR and DE translations
    created_cheese = multilingual_article(
        title="Cheese",
        slug="cheese",
        langs=["fr", "de"],
        fill_categories=[ping],
        contents={
            "fr": {
                "title": "Fromage",
                "slug": "fromage",
                "fill_categories": [ping],
            },
            "de": {
                "title": "Käse",
                "slug": "kase",
                "fill_categories": [ping],
            }
        },
    )

    template = Template(
        "{% load lotus %}{% get_article_languages article_object %}"
    )

    context = Context({
        "article_object": created_cheese["original"],
    })

    with pytest.raises(TemplateSyntaxError) as excinfo:
        template.render(context)

    assert str(excinfo.value) == (
        "'get_article_languages' require either a context variable 'lotus_now' "
        "to be set or a tag argument named 'now'."
    )


def test_tag_get_article_languages_basic(db):
    """
    Tag "get_article_languages" should correctly build HTML with all article
    translations depending arguments given and template context.
    """
    default_tz = pytz.timezone("UTC")
    now = default_tz.localize(datetime.datetime(2012, 10, 15, 10, 0))
    today = default_tz.localize(datetime.datetime(2012, 10, 15, 9, 55))
    tomorrow = default_tz.localize(datetime.datetime(2012, 10, 16, 10, 0))


    # Create cheese articles with published FR and DE translations
    created_cheese = multilingual_article(
        title="Cheese",
        slug="cheese",
        langs=["fr", "de"],
        publish_date=today.date(),
        publish_time=today.time(),
        contents={
            "fr": {
                "title": "Fromage",
                "slug": "fromage",
            },
            "de": {
                "title": "Käse",
                "slug": "kase",
                "publish_date": tomorrow.date(),
                "publish_time": tomorrow.time(),
            }
        },
    )

    template = Template(
        "{% load lotus %}{% get_article_languages article_object %}"
    )

    # Without admin mode, results are filtered on publication criterias
    rendered = template.render(
        Context({
            "article_object": created_cheese["original"],
            "lotus_now": now,
            ADMINMODE_CONTEXTVAR: False,
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["fr"]

    # In admin mode, no filter on publication criterias
    rendered = template.render(
        Context({
            "article_object": created_cheese["original"],
            "lotus_now": now,
            ADMINMODE_CONTEXTVAR: True,
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["de", "fr"]

    # Alike previous but on a translation instead of original
    rendered = template.render(
        Context({
            "article_object": created_cheese["translations"]["fr"],
            "lotus_now": now,
            ADMINMODE_CONTEXTVAR: True,
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["de", "en"]

    # Tag argument "now" can be passed to override context var "lotus_now" and use
    # another date
    template = Template(
        "{% load lotus %}{% get_article_languages article_object now=custom_now %}"
    )
    rendered = template.render(
        Context({
            "article_object": created_cheese["original"],
            "lotus_now": now,
            "custom_now": tomorrow,
            ADMINMODE_CONTEXTVAR: False,
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["de", "fr"]

    # Custom template path can be given and obviously raise an exception if given path
    # cannot be found
    template = Template(
        "{% load lotus %}"
        "{% get_article_languages article_object template='foo/bar/nope.html' %}"
    )

    with pytest.raises(TemplateDoesNotExist):
        rendered = template.render(
            Context({
                "article_object": created_cheese["original"],
                "lotus_now": now,
                ADMINMODE_CONTEXTVAR: False,
            })
        )
