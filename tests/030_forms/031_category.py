from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile

from lotus.factories import ArticleFactory, CategoryFactory
from lotus.forms import CategoryAdminForm
from lotus.models import Category
from lotus.utils.tests import (
    DUMMY_GIF_BYTES, html_pyquery, compact_form_errors, build_post_data_from_object,
)


def test_category_admin_change_form(db):
    """
    Ensure the admin change form is working well (this should cover add form
    also) and ensure image upload is correct.
    """
    # Create new object without a cover file
    obj = CategoryFactory(cover=None)

    # Build initial POST data
    ignore = ["id", "category", "articles"]
    data = build_post_data_from_object(Category, obj, ignore=ignore, extra={
        "_position": "sorted-child",
    })

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
    assert Path(obj.cover.path).exists() is True


def test_category_admin_original_validation(db):
    """
    Changing language should not allow to trick constraint on original relation
    which must be in different language.
    """
    # Create new object without a cover file
    obj_fr = CategoryFactory(language="fr", original=None)
    obj_en = CategoryFactory(language="en", original=None)

    # Build initial POST data
    ignore = ["id", "category", "articles"]
    data = build_post_data_from_object(Category, obj_fr, ignore=ignore, extra={
        "_position": "sorted-child",
    })

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


def test_category_admin_original_translation_validation(db):
    """
    An original category should not be set as a translation of another original.
    """
    # Create new objects
    obj_fr = CategoryFactory(language="fr", original=None)
    bis_en = CategoryFactory(language="en", original=None)
    CategoryFactory(language="en", original=obj_fr)

    # Build initial POST data
    ignore = ["id", "category", "articles"]
    data = build_post_data_from_object(Category, obj_fr, ignore=ignore, extra={
        "_position": "sorted-child",
    })

    data["original"] = bis_en
    f = CategoryAdminForm(data, instance=obj_fr)
    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "original": ["invalid-original"],
    }


def test_category_admin_article_relations_validation(db):
    """
    Category admin form should not allow to change language if object already
    have related articles in different language.
    """
    build_fr = CategoryFactory.build()

    # Build initial POST data
    ignore = ["id", "category", "articles"]
    data = build_post_data_from_object(Category, build_fr, ignore=ignore, extra={
        "_position": "sorted-child",
    })

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


def test_category_admin_create_labels(db):
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


def test_category_admin_change_labels(db):
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


def test_category_admin_form_parent_constraints(db, settings):
    """
    When user try to select a parent in different language than the current category
    itself this should trigger a form validation error.
    """
    settings.LANGUAGE_CODE = "en"

    ignored = ["id", "category", "articles"]

    egg_object = CategoryFactory(title="egg", language="en")
    oeuf_object = CategoryFactory(title="oeuf", language="fr")

    omelette_build = CategoryFactory.build(title="omelette", language="fr")

    # Try to save object with a parent category with a different language will fail
    f = CategoryAdminForm(
        build_post_data_from_object(Category, omelette_build, ignore=ignored, extra={
            "_ref_node_id": egg_object.id,
            "_position": "sorted-child",
        })
    )
    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "_ref_node_id": ["invalid"],
        "language": ["invalid"],
    }

    # Try to save object with a parent category the same language will succeed
    f = CategoryAdminForm(
        build_post_data_from_object(Category, omelette_build, ignore=ignored, extra={
            "_ref_node_id": oeuf_object.id,
            "_position": "sorted-child",
        })
    )
    assert f.is_valid() is True


def test_category_admin_form_parent_descendants(db, settings, tests_settings):
    """
    Language should not be changed if current category has descendants with
    another language than the new selected one.
    """
    settings.LANGUAGE_CODE = "en"

    ignored = ["id", "category", "articles"]

    # Start with some root objects
    CategoryFactory(title="Egg", language="en")
    oeuf_object = CategoryFactory(title="Oeuf", language="fr")
    omelette_object = CategoryFactory(title="Omelette", language="fr")
    victoria_object = CategoryFactory(title="Omelette Victoria", language="fr")

    # Make 'Omelette' as a child of 'Oeuf'
    omelette_object.move_into(oeuf_object)
    omelette_object.refresh_from_db()
    # Make 'Victoria' as a child of 'Omelette'
    victoria_object.move_into(omelette_object)
    victoria_object.refresh_from_db()

    # Try to save Oeuf object with a different language will fail since of its
    # descendants language
    f = CategoryAdminForm(
        build_post_data_from_object(Category, oeuf_object, ignore=ignored, extra={
            "_position": "sorted-child",
            "language": "en",
        }),
        instance=oeuf_object,
    )
    is_valid = f.is_valid()

    assert is_valid is False
    assert compact_form_errors(f) == {
        "language": ["invalid-language"],
    }
