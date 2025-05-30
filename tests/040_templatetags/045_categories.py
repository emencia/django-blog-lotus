import json

import pytest

from django.template import Context, Template, TemplateSyntaxError
from django.test.html import parse_html

from lotus.models import Category
from lotus.factories import CategoryFactory
from lotus.templatetags.lotus import get_categories, get_category_tree_html
from lotus.utils.tests import html_pyquery


def test_languages(db, rf):
    """
    Tag should only list categories for the current request language and possibly
    flag item as "active" if a current category is given and match.
    """
    request = rf.get("/")

    picsou = CategoryFactory(title="Picsou", slug="picsou", language="en")
    CategoryFactory(title="Donald", slug="donald", language="en")
    CategoryFactory(title="Dupont", slug="dupont", language="fr")

    request.LANGUAGE_CODE = "en"
    rendered = get_categories({"request": request}, current=picsou)
    assert rendered == {
        "categories": [
            {
                "title": "Donald",
                "url": "/en/categories/donald/",
                "is_active": False,
            },
            {
                "title": "Picsou",
                "url": "/en/categories/picsou/",
                "is_active": True,
            }
        ]
    }

    request.LANGUAGE_CODE = "fr"
    rendered = get_categories({"request": request}, current=picsou)
    assert rendered == {
        "categories": [
            {
                "title": "Dupont",
                "url": "/fr/categories/dupont/",
                "is_active": False,
            },
        ]
    }

    request.LANGUAGE_CODE = "de"
    rendered = get_categories({"request": request})
    assert rendered == {
        "categories": []
    }


def test_unavailable_language(db, rf):
    """
    Tag should not fail when current language is unknow, it just return empty result.
    """
    request = rf.get("/")
    request.LANGUAGE_CODE = "zh"

    CategoryFactory(title="Picsou", slug="picsou", language="en")

    rendered = get_categories({"request": request})
    assert len(rendered["categories"]) == 0


def test_current_invalid(db, rf):
    """
    Tag should raise a TemplateSyntaxError if given current argument is not a
    Category object.
    """
    request = rf.get("/")

    CategoryFactory(title="Picsou", slug="picsou", language="en")

    request.LANGUAGE_CODE = "en"

    with pytest.raises(TemplateSyntaxError) as excinfo:
        get_categories({"request": request}, current=42)

    assert str(excinfo.value) == (
        "'get_categories' tag only accepts a Category object as 'current' argument. "
        "Object type 'int' was given."
    )


def test_template_rendering(db, rf):
    """
    HTML tag rendering test in-situ in a basic template.
    """
    request = rf.get("/")
    request.LANGUAGE_CODE = "en"

    picsou = CategoryFactory(title="Picsou", slug="picsou", language="en")
    donald = CategoryFactory(title="Donald", slug="donald", language="en")
    CategoryFactory(title="Dupont", slug="dupont", language="fr")

    template_to_render = Template("{% load lotus %}{% get_categories_html picsou %}")
    rendered_template = template_to_render.render(
        Context({"request": request, "picsou": picsou})
    )

    # Expected items are in built HTML
    dom = html_pyquery(rendered_template)
    assert sorted([
        (a.text.strip(), a.get("href"), a.get("aria-current"))
        for a in dom.find("a")
    ]) == [
        ("Donald", donald.get_absolute_url(), None),
        ("Picsou", picsou.get_absolute_url(), "page"),
    ]


def test_tree_rendering(tests_settings, db, rf):
    """
    Tag 'get_category_tree_html' should recursively list the Category tree.
    """
    request = rf.get("/")
    request.LANGUAGE_CODE = "en"

    sample_path = (
        tests_settings.fixtures_path / "category_tree_basic.json"
    )
    sample = json.loads(sample_path.read_text())

    Category.load_bulk(sample["tree"])
    rendered_template = get_category_tree_html({"request": request})

    expected = (
        '<nav class="nav">'
        '   <ul class="tree">'
        '       <li class="item"><a href="/en/categories/item-1/">Item 1</a></li>'
        '       <li class="item has-children">'
        '           <a href="/en/categories/item-2/">Item 2</a>'
        '           <ul class="nodes">'
        '               <li class="item has-children">'
        '                   <a href="/en/categories/item-2-1/">Item 2.1</a>'
        '                   <ul class="nodes">'
        '                       <li class="item">'
        '                           <a href="/en/categories/item-2-1-1/">Item 2.1.1</a>'
        '                       </li>'
        '                   </ul>'
        '               </li>'
        '           </ul>'
        '       </li>'
        '   </ul>'
        '</nav>'
    )

    assert parse_html(rendered_template) == parse_html(expected)
