import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from lotus.factories import multilingual_category, ArticleFactory, CategoryFactory
from lotus.forms import CategoryAdminForm
from lotus.models import Category
from lotus.utils.tests import (
    DUMMY_GIF_BYTES, html_pyquery, compact_form_errors, build_post_data_from_object,
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
)


def test_category_admin_add(db, admin_client):
    """
    Category model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(Category)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_list(db, admin_client):
    """
    Category model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(Category)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_detail(db, admin_client):
    """
    Category model admin detail view should not raise error on GET request.
    """
    obj = CategoryFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_category_admin_change_form(db, admin_client):
    """
    Ensure the admin change form is working well (this should cover add form
    also) and ensure image upload is correct.
    """
    # Create new object without a cover file
    obj = CategoryFactory(cover=None)

    # Build initial POST data
    ignore = ["id", "category", "articles"]
    data = build_post_data_from_object(Category, obj, ignore=ignore)

    file_data = {
        "cover": SimpleUploadedFile(
            "small.gif",
            DUMMY_GIF_BYTES,
            content_type="image/gif"
        ),
    }

    f = CategoryAdminForm(data, file_data, instance=obj)

    # No validation errors
    assert f.is_valid() is True
    assert f.errors.as_data() == {}

    updated_obj = f.save()

    # Check everything has been saved
    assert updated_obj.title == obj.title
    assert os.path.exists(obj.cover.path) is True


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


def test_category_admin_original_validation(db, admin_client):
    """
    Changing language should not allow to trick constraint on original relation
    which must be in different language.
    """
    # Create new object without a cover file
    obj_fr = CategoryFactory(language="fr", original=None)
    obj_en = CategoryFactory(language="en", original=None)

    # Build initial POST data
    ignore = ["id", "category", "articles"]
    data = build_post_data_from_object(Category, obj_fr, ignore=ignore)

    # 1) Edit to set original on 'obj_en', everything is ok
    data["original"] = obj_en
    f = CategoryAdminForm(data, instance=obj_fr)

    # No validation errors
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}
    assert obj_fr.original.language != obj_fr.language

    obj_fr = f.save()

    # 2) Switch language to 'EN' should not allow to keep the original relation
    # on 'obj_en' in 'EN' language
    data["language"] = "en"
    f = CategoryAdminForm(data, instance=obj_fr)

    # Validation is raised on language field
    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "language": ["invalid"],
        "original": ["invalid"],
    }


def test_category_admin_article_relations_validation(db, admin_client):
    """
    Category admin form should not allow to change language if object already
    have related articles in different language.
    """
    build_fr = CategoryFactory.build()

    # Build initial POST data
    ignore = ["id", "category", "articles"]
    data = build_post_data_from_object(Category, build_fr, ignore=ignore)

    # 1) Set category without any article relation yet
    data["language"] = "fr"

    f = CategoryAdminForm(data)
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    cat_fr = f.save()

    # Set an article relation
    ArticleFactory(language="fr", fill_categories=[cat_fr])

    # 2) Change language to a different one from related articles
    data["language"] = "en"

    f = CategoryAdminForm(data, instance=cat_fr)
    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "language": ["invalid-language"],
    }


def test_category_admin_modelchoice_create_labels(db, admin_client):
    """
    Admin create form should have language names in model choices fields.
    """
    # Create new objects
    CategoryFactory(title="egg", language="en")
    CategoryFactory(title="baguette", language="fr")

    # Build form and get its simple HTML representation to parse it
    f = CategoryAdminForm()
    content = f.as_p()
    dom = html_pyquery(content)

    originals = dom.find("#id_original option")
    assert [item.text for item in originals] == [
        f.fields["original"].empty_label,
        "baguette [Français]",
        "egg [English]",
    ]


def test_category_admin_modelchoice_change_labels(db, admin_client):
    """
    Admin change form should have language names in model choices fields.
    """
    # Create new objects
    CategoryFactory(title="egg", language="en")
    obj_fr = CategoryFactory(title="baguette", language="fr")
    CategoryFactory(title="omelette", language="fr")

    # Build form and get its simple HTML representation to parse it
    f = CategoryAdminForm({}, instance=obj_fr)
    content = f.as_p()
    dom = html_pyquery(content)

    originals = dom.find("#id_original option")
    assert [item.text for item in originals] == [
        f.fields["original"].empty_label,
        "egg [English]",
    ]


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
