from lotus.factories import CategoryFactory, multilingual_category
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

    # Use default language as configured in settings
    assert queryset_values(Category.objects.get_for_lang()) == [
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
