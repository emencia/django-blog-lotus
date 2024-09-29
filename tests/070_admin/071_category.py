import json

from django.urls import reverse

from lotus.factories import multilingual_category, CategoryFactory
from lotus.forms import CategoryAdminForm
from lotus.models import Category
from lotus.utils.tests import (
    html_pyquery, get_admin_add_url, get_admin_change_url, get_admin_list_url,
)


def test_category_admin_ping_add(db, admin_client):
    """
    Category model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(Category)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_ping_list(db, admin_client):
    """
    Category model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(Category)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_ping_detail(db, admin_client):
    """
    Category model admin detail view should not raise error on GET request.
    """
    obj = CategoryFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_original_choices(db, admin_client):
    """
    Choices for 'original' should not list item in same language, not the
    category itself and only original articles.
    """
    # Create new object to check
    obj = CategoryFactory(language="en")
    # Create new object as a translation
    CategoryFactory(language="fr", original=obj)
    # Create some objects in same language
    CategoryFactory(language="en")
    CategoryFactory(language="en")
    # Create some other objects in various other languages, these are the only
    # elligible categories for original field choices
    fillers_langs = [
        CategoryFactory(language="fr"),
        CategoryFactory(language="fr"),
        CategoryFactory(language="de"),
    ]

    # Get the obj detail page
    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200

    dom = html_pyquery(response)

    # Get available choice ids from their values
    options = dom.find("#id_original option")
    option_ids = [int(item.get("value")) for item in options if item.get("value")]

    assert sorted(option_ids) == sorted([item.id for item in fillers_langs])


def test_category_admin_translate_button_empty(db, admin_client):
    """
    Translate button should not be in detail if there is no available language for
    translation and finally the translate page should not contain form since there is
    language available.
    """
    # Create cheese categories with published FR and DE translations
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

    # No translate button expected since all possible languages have been used
    url = get_admin_change_url(created_cheese["original"])
    response = admin_client.get(url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    links = dom.find(".lotus-translate-link")
    assert len(links) == 0

    # Expected existing translation languages (without the original language)
    existings = dom.find(".lotus-siblings-resume a")
    assert len(existings) == 2

    existing_languages = [item.get("data-lotus-langcode") for item in existings]
    assert sorted(existing_languages) == ["de", "fr"]

    # No form expected since there is no available languages
    url = reverse(
        "admin:lotus_category_translate_original",
        args=(created_cheese["original"].id,),
    )
    response = admin_client.get(url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    forms = dom.find("#lotus-translate-original-form")
    assert len(forms) == 0


def test_category_admin_translate_button_expected(db, admin_client):
    """
    Translate button should be in detail page with the right URL and lead to the
    "Translate" form with the right available languages.
    """
    # Create meat categories with a single DE translation
    created_beef = multilingual_category(
        title="Beef",
        slug="beef",
        langs=["de"],
        contents={
            "de": {
                "title": "Rindfleisch",
                "slug": "rindfleisch",
            }
        },
    )

    # Translate button is expected since there is an available language to translate to
    url = get_admin_change_url(created_beef["original"])
    response = admin_client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)

    existings = dom.find(".lotus-siblings-resume a")
    assert len(existings) == 1

    links = dom.find(".lotus-translate-link")
    assert len(links) == 1

    # Expected existing translation languages (without the original language)
    existing_languages = [item.get("data-lotus-langcode") for item in existings]
    assert sorted(existing_languages) == ["de"]

    response = admin_client.get(links[0].get("href"))
    assert response.status_code == 200

    # Form is expected since there is an available language. Directly use the URL from
    # translate button
    dom = html_pyquery(response)
    forms = dom.find("#lotus-translate-original-form")
    assert len(forms) == 1

    # Check expected available language is correct
    options = dom.find("#lotus-translate-original-form #id_language option")
    option_ids = [item.get("value") for item in options if item.get("value")]
    assert sorted(option_ids) == ["fr"]

    # Ensure the original id is correctly set into hidden input
    original_id = dom.find("#lotus-translate-original-form input[name='original']")
    assert len(original_id) == 1
    assert int(original_id[0].get("value")) == created_beef["original"].id


def test_category_admin_form_parent_select(settings, tests_settings, db, admin_client):
    """
    Parent field should correctly list available categories with a tree alike display.

    Note how all languages are listed since we need user to be able to switch to another
    one when possible.
    """
    settings.LANGUAGE_CODE = "en"

    sample = json.loads(
        (tests_settings.fixtures_path / "category_tree.json").read_text()
    )
    Category.load_bulk(sample["tree"])

    # In creation form the select input lists all categories
    url = get_admin_add_url(Category)
    response = admin_client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)
    # print(json.dumps(
    #     [item.text for item in dom.find("#id__ref_node_id option")],
    #     indent=4,
    #     ensure_ascii=False
    # ))
    assert [item.text for item in dom.find("#id__ref_node_id option")] == [
        CategoryAdminForm.PARENT_EMPTY_LABEL,
        "Item 1 [English]",
        "└── Item 1.1 [English]",
        "Item 2 [English]",
        "Item 3 [English]",
        "└── Item 3.1 [English]",
        "        └── Item 3.1.1 [English]",
        "        └── Item 3.1.2 [English]",
        "        └── Item 3.1.3 [English]",
        "        └── Item 3.1.4 [Français]",
        "└── Item 3.2 [English]"
    ]

    # In edition form current category is excluded from options
    item_1 = Category.objects.get(slug="item-1")
    url = get_admin_change_url(item_1)
    response = admin_client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)

    assert [item.text for item in dom.find("#id__ref_node_id option")] == [
        CategoryAdminForm.PARENT_EMPTY_LABEL,
        "Item 2 [English]",
        "Item 3 [English]",
        "└── Item 3.1 [English]",
        "        └── Item 3.1.1 [English]",
        "        └── Item 3.1.2 [English]",
        "        └── Item 3.1.3 [English]",
        "        └── Item 3.1.4 [Français]",
        "└── Item 3.2 [English]"
    ]

    # In edition form current category and its descendants are excluded from options
    item_3 = Category.objects.get(slug="item-3")
    url = get_admin_change_url(item_3)
    response = admin_client.get(url)
    assert response.status_code == 200
    dom = html_pyquery(response)
    assert [item.text for item in dom.find("#id__ref_node_id option")] == [
        CategoryAdminForm.PARENT_EMPTY_LABEL,
        "Item 1 [English]",
        "└── Item 1.1 [English]",
        "Item 2 [English]"
    ]
