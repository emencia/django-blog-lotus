import datetime

import pytest

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.template import (
    Context, Template, TemplateSyntaxError, TemplateDoesNotExist,
)

from lotus.factories import (
    AuthorFactory, CategoryFactory,
    multilingual_article, multilingual_category
)
from lotus.utils.tests import html_pyquery
from lotus.templatetags.lotus import translation_siblings


def test_tag_translation_siblings_allowed_models(db):
    """
    Tag "translation_siblings" is only implemented for Article and Category.
    """
    foo = AuthorFactory()

    with pytest.raises(TemplateSyntaxError) as excinfo:
        translation_siblings(Context(), foo)

    assert str(excinfo.value) == (
        "'translation_siblings' only accepts a Category or Article object for "
        "'source' argument. Object type 'Author' was given."
    )


def test_tag_translation_siblings_html_allowed_models(db):
    """
    Ensure the error message contain the right tag name.
    """
    foo = AuthorFactory()

    template = Template(
        "{% load lotus %}{% translation_siblings_html article_object %}"
    )

    with pytest.raises(TemplateSyntaxError) as excinfo:
        template.render(
            Context({
                "article_object": foo,
            })
        )

    assert str(excinfo.value) == (
        "'translation_siblings_html' only accepts a Category or Article object for "
        "'source' argument. Object type 'Author' was given."
    )


def test_tag_translation_siblings_missing_now(db):
    """
    Tag "translation_siblings" requires an article object and context variable
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

    with pytest.raises(TemplateSyntaxError) as excinfo:
        translation_siblings(Context(), created_cheese["original"])

    assert str(excinfo.value) == (
        "'translation_siblings' require either a context variable 'lotus_now' "
        "to be set or a tag argument named 'now'."
    )


def test_tag_translation_siblings_article(db, settings):
    """
    Tag "translation_siblings" should correctly build HTML with all article
    translations depending arguments given and template context.
    """
    utc = ZoneInfo("UTC")
    now = datetime.datetime(2012, 10, 15, 10, 0).replace(tzinfo=utc)
    today = datetime.datetime(2012, 10, 15, 9, 55).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    # Create cheese articles with published FR translation and unplished (yet) DE
    # translation
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

    # Without preview mode, results are filtered on publication criterias
    context = Context({
        "lotus_now": now,
        settings.LOTUS_PREVIEW_VARNAME: False,
    })
    output = translation_siblings(context, created_cheese["original"])
    assert output["source"] == created_cheese["original"]
    assert list(output["siblings"]) == [
        created_cheese["translations"]["fr"],
    ]
    assert sorted(output["existing_languages"]) == ["en", "fr"]
    assert sorted(output["available_languages"]) == ["de"]

    # In preview mode, no filter on publication criterias
    context = Context({
        "lotus_now": now,
        settings.LOTUS_PREVIEW_VARNAME: True,
    })
    output = translation_siblings(context, created_cheese["original"])
    assert output["source"] == created_cheese["original"]
    assert list(output["siblings"]) == [
        created_cheese["translations"]["de"],
        created_cheese["translations"]["fr"],
    ]
    assert sorted(output["existing_languages"]) == ["de", "en", "fr"]
    assert sorted(output["available_languages"]) == []

    # Alike previous but on a translation instead of original
    context = Context({
        "lotus_now": now,
        settings.LOTUS_PREVIEW_VARNAME: True,
    })
    output = translation_siblings(context, created_cheese["translations"]["fr"])
    assert output["source"] == created_cheese["translations"]["fr"]
    assert list(output["siblings"]) == [
        created_cheese["translations"]["de"],
        created_cheese["original"],
    ]
    assert sorted(output["existing_languages"]) == ["de", "en", "fr"]
    assert sorted(output["available_languages"]) == []

    # Tag argument "now" can be passed to override context var "lotus_now" and use
    # another date
    context = Context({
        "lotus_now": now,
        settings.LOTUS_PREVIEW_VARNAME: False,
    })
    output = translation_siblings(context, created_cheese["original"], now=tomorrow)
    assert output["source"] == created_cheese["original"]
    assert list(output["siblings"]) == [
        created_cheese["translations"]["de"],
        created_cheese["translations"]["fr"],
    ]
    assert sorted(output["existing_languages"]) == ["de", "en", "fr"]
    assert sorted(output["available_languages"]) == []


def test_tag_translation_siblings_html_article(db, settings):
    """
    Tag "translation_siblings_html" should correctly build HTML with all article
    translations depending arguments given and template context.
    """
    utc = ZoneInfo("UTC")
    now = datetime.datetime(2012, 10, 15, 10, 0).replace(tzinfo=utc)
    today = datetime.datetime(2012, 10, 15, 9, 55).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    # Create cheese articles with published FR translation and unplished (yet) DE
    # translation
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
        "{% load lotus %}{% translation_siblings_html article_object %}"
    )

    # Without preview mode, results are filtered on publication criterias
    rendered = template.render(
        Context({
            "article_object": created_cheese["original"],
            "lotus_now": now,
            settings.LOTUS_PREVIEW_VARNAME: False,
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["fr"]

    # Custom template path can be given and obviously raise an exception if given path
    # cannot be found
    template = Template(
        "{% load lotus %}"
        "{% translation_siblings_html article_object template='foo/bar/nope.html' %}"
    )

    with pytest.raises(TemplateDoesNotExist):
        rendered = template.render(
            Context({
                "article_object": created_cheese["original"],
                "lotus_now": now,
                settings.LOTUS_PREVIEW_VARNAME: False,
            })
        )


def test_tag_translation_siblings_html_article_bypass(db, settings):
    """
    Tag optional argument "preview" should bypass usage of context variable to
    enable or disable the preview mode.
    """
    utc = ZoneInfo("UTC")
    now = datetime.datetime(2012, 10, 15, 10, 0).replace(tzinfo=utc)
    today = datetime.datetime(2012, 10, 15, 9, 55).replace(tzinfo=utc)
    tomorrow = datetime.datetime(2012, 10, 16, 10, 0).replace(tzinfo=utc)

    # Create cheese articles with published FR translation and unplished (yet) DE
    # translation
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

    # Preview mode is disabled from context but are forced as enabled from tag argument
    template = Template(
        "{% load lotus %}{% translation_siblings_html article_object preview=True %}"
    )

    rendered = template.render(
        Context({
            "article_object": created_cheese["original"],
            "lotus_now": now,
            settings.LOTUS_PREVIEW_VARNAME: False,
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["de", "fr"]

    # Preview mode is enabled from context but are forced as disabled from tag argument
    template = Template(
        "{% load lotus %}"
        "{% translation_siblings_html article_object preview=False %}"
    )

    rendered = template.render(
        Context({
            "article_object": created_cheese["original"],
            "lotus_now": now,
            settings.LOTUS_PREVIEW_VARNAME: True,
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["fr"]


def test_tag_translation_siblings_category(db):
    """
    Tag "translation_siblings" should returns all expected translation siblings.
    """
    # A dummy category just for filling
    CategoryFactory()

    # Create cheese articles with published FR and DE translations
    created_cheese = multilingual_category(
        title="Cheese",
        slug="cheese",
        langs=["fr", "de"],
        contents={
            "fr": {
                "title": "Fromage",
                "slug": "fromage",
            },
            "de": {
                "title": "Käse",
                "slug": "kase",
            }
        },
    )

    output = translation_siblings(Context(), created_cheese["original"])

    assert output["source"] == created_cheese["original"]

    assert list(output["siblings"]) == [
        created_cheese["translations"]["de"],
        created_cheese["translations"]["fr"],
    ]
    assert sorted(output["existing_languages"]) == ["de", "en", "fr"]
    assert sorted(output["available_languages"]) == []


def test_tag_translation_siblings_html_category(db):
    """
    Tag "translation_siblings_html" should correctly build HTML with all category
    translations without needing of lotus_now/now or context variable for preview mode.
    """
    # Create cheese articles with published FR and DE translations
    created_cheese = multilingual_category(
        title="Cheese",
        slug="cheese",
        langs=["fr", "de"],
        contents={
            "fr": {
                "title": "Fromage",
                "slug": "fromage",
            },
            "de": {
                "title": "Käse",
                "slug": "kase",
            }
        },
    )

    template = Template(
        "{% load lotus %}{% translation_siblings_html category_object %}"
    )

    # Without preview mode, results are filtered on publication criterias
    rendered = template.render(
        Context({
            "category_object": created_cheese["original"],
        })
    )
    dom = html_pyquery(rendered)
    items = dom.find(".sibling a")
    assert [item.text for item in items] == ["de", "fr"]
