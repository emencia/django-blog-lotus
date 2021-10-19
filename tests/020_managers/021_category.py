from lotus.factories import (
    CategoryFactory, multilingual_article, multilingual_category,
)
from lotus.models import Category
from lotus.utils.tests import queryset_values


def test_category_managers(db):
    """
    Category manager should be able to correctly filter on language.
    """
    # Simple category on default language without translations
    CategoryFactory(slug="foobar")

    # Original category on different language than 'settings.LANGUAGE_CODE' and
    # with a translation for 'settings.LANGUAGE_CODE' lang.
    multilingual_category(
        slug="musique",
        language="fr",
        langs=["en"],
        contents={
            "en": {
                "slug": "music",
            }
        },
    )

    # A category with a french translation inheriting original slug
    multilingual_category(
        slug="food",
        langs=["fr"],
    )

    # A category with french translation with its own slug and deutsch
    # translation inheriting original slug
    multilingual_category(
        slug="recipe",
        langs=["fr", "de"],
        contents={
            "fr": {
                "slug": "recette",
            }
        },
    )

    # For english language
    assert queryset_values(Category.objects.get_for_lang("en")) == [
        {"slug": "foobar", "language": "en"},
        {"slug": "food", "language": "en"},
        {"slug": "music", "language": "en"},
        {"slug": "recipe", "language": "en"},
    ]

    # For french language
    assert queryset_values(Category.objects.get_for_lang("fr")) == [
        {"slug": "food", "language": "fr"},
        {"slug": "musique", "language": "fr"},
        {"slug": "recette", "language": "fr"},
    ]

    # For deutsch language
    assert queryset_values(Category.objects.get_for_lang("de")) == [
        {"slug": "recipe", "language": "de"},
    ]


def test_category_get_articles(db):
    """
    Demonstrate how to get category related articles correctly using Category manager.
    """
    ping = CategoryFactory()
    pong = CategoryFactory()

    multilingual_article(
        slug="foo",
        langs=["fr"],
        fill_categories=[ping, pong],
        contents={
            "fr": {
                "slug": "fou",
                "fill_categories": [ping, pong],
            }
        },
    )

    multilingual_article(
        slug="bar",
        langs=["fr"],
        fill_categories=[ping],
        contents={
            "fr": {
                "slug": "barre",
                "fill_categories": [ping, pong],
            }
        },
    )

    multilingual_article(
        slug="moo",
        fill_categories=[ping],
    )

    multilingual_article(
        slug="yeah",
        langs=["fr"],
        fill_categories=[pong],
        contents={
            "fr": {
                "slug": "ouais",
                "fill_categories": [ping],
            }
        },
    )

    multilingual_article(slug="nope")

    ping_articles = [
        (item.slug, item.language)
        for item in ping.articles.get_for_lang("en")
    ]

    pong_articles = [
        (item.slug, item.language)
        for item in pong.articles.get_for_lang("en")
    ]

    # Get unordered queryset then order by slug to avoid arbitrary order
    unordered_ping_articles = [
        (item.slug, item.language)
        for item in ping.articles.get_for_lang("en").order_by("slug")
    ]

    assert ping_articles == [
        ("moo", "en"),
        ("bar", "en"),
        ("foo", "en"),
    ]

    assert pong_articles == [
        ("yeah", "en"),
        ("foo", "en"),
    ]

    assert unordered_ping_articles == [
        ("bar", "en"),
        ("foo", "en"),
        ("moo", "en"),
    ]


def test_category_managers_get_siblings(db):
    """
    Manager method "get_siblings" should return all siblings category translations.
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

    # Get all siblings slugs ordered
    cheese_siblings = Category.objects.get_siblings(
        source=created_cheese["original"]
    ).values_list('slug', flat=True).order_by("slug")

    fromage_siblings = Category.objects.get_siblings(
        source=created_cheese["translations"]["fr"]
    ).values_list('slug', flat=True).order_by("slug")

    kase_siblings = Category.objects.get_siblings(
        source=created_cheese["translations"]["de"]
    ).values_list('slug', flat=True).order_by("slug")

    assert list(cheese_siblings) == [
        "fromage", "kase",
    ]
    assert list(fromage_siblings) == [
        "cheese", "kase",
    ]
    assert list(kase_siblings) == [
        "cheese", "fromage",
    ]
