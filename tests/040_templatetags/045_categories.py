import pytest

from django.template import Context, Template
from django.utils import translation

from lotus.factories import CategoryFactory
from lotus.templatetags.lotus import article_categories


def assert_rendered_context(en_categories, rendered):
    for category in en_categories:
        assert {
                "title": category.title,
                "url": category.get_absolute_url()
            } in rendered["categories"]


def test_english_language(db):

    with translation.override("en"):
        en_categories = CategoryFactory.create_batch(3, language="en")
        rendered = article_categories()

        assert len(rendered["categories"]) == 3
        assert_rendered_context(en_categories, rendered)


def test_french_language(db):
    with translation.override("fr"):
        fr_categories = CategoryFactory.create_batch(3, language="fr")
        rendered = article_categories()

        assert len(rendered["categories"]) == 3
        assert_rendered_context(fr_categories, rendered)


def test_no_categories(db):
    with translation.override("en"):
        rendered = article_categories()

        assert len(rendered["categories"]) == 0


def test_multiple_languages(db):
    en_categories = CategoryFactory.create_batch(3, language="en")
    fr_categories = CategoryFactory.create_batch(3, language="fr")

    with translation.override("en"):
        rendered = article_categories()
        assert len(rendered["categories"]) == 3
        assert_rendered_context(en_categories, rendered)

    with translation.override("fr"):
        rendered = article_categories()
        assert len(rendered["categories"]) == 3
        assert_rendered_context(fr_categories, rendered)


def test_unavailable_language(db):
    CategoryFactory.create_batch(3, language="en")

    # Set the language without categories
    with translation.override("de"):
        rendered = article_categories()
        assert len(rendered["categories"]) == 0


def test_categories_ordering(db):
    en_categories = CategoryFactory.create_batch(5, language="en")

    with translation.override("en"):
        rendered = article_categories()
        assert len(rendered["categories"]) == 5

        rendered_titles = [category["title"] for category in rendered["categories"]]
        original_titles = sorted([category.title for category in en_categories])

        # Verify that the categories are ordered by title
        assert rendered_titles == original_titles


def test_template_rendering(db):
    en_categories = CategoryFactory.create_batch(3, language="en")

    with translation.override("en"):
        categories = article_categories()
        context = Context(categories)
        template_to_render = Template(
            "{% load lotus %}{% news_categories %}"
        )
        rendered_template = template_to_render.render(context)

        for category in en_categories:
            assert f'href="{category.get_absolute_url()}"' in rendered_template
            assert category.title in rendered_template
