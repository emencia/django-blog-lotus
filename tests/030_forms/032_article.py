from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile

from lotus.factories import ArticleFactory, CategoryFactory
from lotus.forms import ArticleAdminForm
from lotus.models import Article
from lotus.utils.tests import (
    DUMMY_GIF_BYTES, html_pyquery, compact_form_errors, build_post_data_from_object,
)


def test_article_admin_change_form(db):
    """
    Ensure the admin change form is working well (this should cover add form
    also) and ensure image upload is correct.
    """
    # Create new object without a cover file
    obj = ArticleFactory(
        cover=None,
        image=None,
        fill_categories=True,
        fill_authors=True,
        fill_tags=True,
    )

    # Fields we don't want to post anything
    ignored_fields = ["id", "relations", "article", "tagged_items"]

    # Build POST data from object field values
    data = {}
    fields = [
        f.name for f in Article._meta.get_fields()
        if f.name not in ignored_fields
    ]
    for name in fields:
        value = getattr(obj, name)
        # M2M are special ones since form expect only a list of IDs
        if name in ("categories", "authors", "related"):
            data[name] = value.values_list("id", flat=True)
        # Tags is a very special field, a list of tag names is expected
        elif name in ("tags",):
            data[name] = list(value.names())
        else:
            data[name] = value

    file_data = {
        "cover": SimpleUploadedFile(
            "small.gif",
            DUMMY_GIF_BYTES,
            content_type="image/gif"
        ),
        "image": SimpleUploadedFile(
            "large.gif",
            DUMMY_GIF_BYTES,
            content_type="image/gif"
        ),
    }

    f = ArticleAdminForm(data, file_data, instance=obj)

    # No validation errors
    assert f.is_valid() is True
    assert f.errors.as_data() == {}

    updated_obj = f.save()

    # Check everything has been saved
    assert updated_obj.title == obj.title
    assert Path(obj.cover.path).exists() is True
    assert Path(obj.image.path).exists() is True


def test_article_admin_original_validation(db):
    """
    Changing language should not allow to trick constraint on original relation
    which must be in different language.
    """
    # Create new object without a cover file
    obj_a = ArticleFactory(language="fr")
    obj_b = ArticleFactory(language="en")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories", "tags",
    ]
    data = build_post_data_from_object(
        Article, obj_a, ignore=ignore, extra={"tags": []}
    )

    # 1) Edit to set original on 'obj_b', everything is ok
    data["original"] = obj_b

    f = ArticleAdminForm(data, instance=obj_a)

    # No validation errors
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}
    assert obj_a.original.language != obj_a.language

    obj_a = f.save()

    # 2) Switch language to 'EN' should not allow to keep the original relation
    # on 'obj_b' in 'EN' language
    data["language"] = "en"
    f = ArticleAdminForm(data, instance=obj_a)

    # Validation is raised on language field
    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "language": ["invalid"],
        "original": ["invalid"],
    }


def test_article_admin_original_add_validation(db):
    """
    Just add an original in different language should work.
    """
    # Create new objects
    obj_fr = ArticleFactory(language="fr")
    obj_en = ArticleFactory(language="en")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories", "tags",
    ]
    data = build_post_data_from_object(
        Article, obj_fr, ignore=ignore, extra={"tags": []}
    )

    data["original"] = obj_en

    f = ArticleAdminForm(data, instance=obj_fr)
    # No validation errors
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}
    assert obj_fr.original.language != obj_fr.language

    obj_fr = f.save()


def test_article_admin_original_change_validation(db):
    """
    Changing language should not allow to trick constraint on original relation
    which must be in different language.
    """
    # Create new objects
    obj_en = ArticleFactory(language="en")
    obj_fr = ArticleFactory(language="fr", original=obj_en)

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories", "tags",
    ]
    data = build_post_data_from_object(
        Article, obj_fr, ignore=ignore, extra={"tags": []}
    )

    # Trying to switch language to 'EN' should not allow to keep the original
    # relation on 'obj_en' in 'EN' language
    data["language"] = "en"
    f = ArticleAdminForm(data, instance=obj_fr)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "language": ["invalid"],
        "original": ["invalid"],
    }


def test_article_admin_related_create_validation(db):
    """
    Admin create form should not allow to set related article with a different
    language.
    """
    # Create new objects
    obj_en = ArticleFactory(language="en")
    obj_fr = ArticleFactory(language="fr")
    # Build object to create
    build_fr = ArticleFactory.build(language="fr")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories", "tags",
    ]
    data = build_post_data_from_object(
        Article, build_fr, ignore=ignore, extra={"tags": []}
    )

    # 1) Try to add related article in different language, raise error
    data["related"] = [obj_en.id]

    f = ArticleAdminForm(data)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "related": ["invalid-related"],
    }

    # 2) Correctly add related article with same language, should work
    data["related"] = [obj_fr.id]

    f = ArticleAdminForm(data)

    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    obj_fr_bis = f.save()

    assert obj_fr_bis.related.all().count() == 1


def test_article_admin_related_change_validation(db):
    """
    Admin change form should not allow to set related article with a different
    language.
    """
    # Create new objects
    obj_en = ArticleFactory(language="en")
    obj_en_bis = ArticleFactory(language="en")
    obj_fr = ArticleFactory(language="fr")
    obj_fr_bis = ArticleFactory(language="fr")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories", "tags",
    ]
    data = build_post_data_from_object(
        Article, obj_fr, ignore=ignore, extra={"tags": []}
    )

    # 1) Try to add related article in different language, raise error
    data["related"] = [obj_en.id]

    f = ArticleAdminForm(data, instance=obj_fr)
    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "related": ["invalid_choice"],
    }

    # 2) Try to add related article in same language, should be ok
    data["related"] = [obj_fr_bis.id]

    f = ArticleAdminForm(data, instance=obj_fr)

    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    # Save it for next test part
    obj_fr = f.save()

    # 3) Try again to add related article in different language, keep raising
    # error
    data["related"] = [obj_fr_bis.id, obj_en_bis.id]

    f = ArticleAdminForm(data, instance=obj_fr)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "related": ["invalid_choice"],
    }

    # 4) Restore working related object in same language
    data["related"] = [obj_fr_bis.id]
    f = ArticleAdminForm(data, instance=obj_fr)
    obj_fr = f.save()

    # 5) Try to change language with remaining related object in a different
    # language, raise an error
    data["language"] = "en"

    f = ArticleAdminForm(data, instance=obj_fr)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "related": ["invalid-related"],
    }


def test_article_admin_category_create_validation(db):
    """
    Admin create form should not allow to set category with a different
    language.
    """
    cat_en = CategoryFactory(language="en")
    cat_fr = CategoryFactory(language="fr")
    # Build object to create
    build_fr = ArticleFactory.build(language="fr")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories", "tags",
    ]
    data = build_post_data_from_object(
        Article, build_fr, ignore=ignore, extra={"tags": []}
    )

    # 1) Try to add category in different language, raise error
    data["categories"] = [cat_en.id]

    f = ArticleAdminForm(data)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "categories": ["invalid-categories"],
    }

    # 2) Correctly add category with same language, should work
    data["categories"] = [cat_fr.id]

    f = ArticleAdminForm(data)

    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    obj_fr_bis = f.save()

    assert obj_fr_bis.categories.all().count() == 1


def test_article_admin_category_change_validation(db):
    """
    Admin change form should not allow to set category with a different
    language.
    """
    cat_en = CategoryFactory(language="en")
    cat_fr = CategoryFactory(language="fr")
    obj_fr = ArticleFactory(language="fr")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories", "tags",
    ]
    data = build_post_data_from_object(
        Article, obj_fr, ignore=ignore, extra={"tags": []}
    )

    # 1) Try to add category in different language, raise error
    data["categories"] = [cat_en.id]

    f = ArticleAdminForm(data, instance=obj_fr)
    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "categories": ["invalid_choice"],
    }

    # 2) Try to add category in same language, should be ok
    data["categories"] = [cat_fr.id]

    f = ArticleAdminForm(data, instance=obj_fr)
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}

    # Save it for next test part
    obj_fr = f.save()

    # 3) Try again to add category in different language, keep raising
    # error
    data["categories"] = [cat_fr.id, cat_en.id]

    f = ArticleAdminForm(data, instance=obj_fr)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "categories": ["invalid_choice"],
    }

    # 4) Restore working category object in same language
    data["categories"] = [cat_fr.id]
    f = ArticleAdminForm(data, instance=obj_fr)
    obj_fr = f.save()

    # 5) Try to change language with remaining category object in a different
    # language, raise an error
    data["language"] = "en"

    f = ArticleAdminForm(data, instance=obj_fr)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "categories": ["invalid-categories"],
    }


def test_article_preview_modelchoice_create_labels(db):
    """
    Admin create form should have language names in model choices fields.
    """
    # Create new objects
    CategoryFactory(title="garlic", language="en")
    CategoryFactory(title="ail", language="fr")

    ArticleFactory(title="egg", language="en")
    ArticleFactory(title="baguette", language="fr")

    # Build form and get its simple HTML representation to parse it
    f = ArticleAdminForm()
    content = f.as_p()
    dom = html_pyquery(content)

    originals = dom.find("#id_original option")
    assert [item.text for item in originals] == [
        f.fields["original"].empty_label,
        "baguette [Français]",
        "egg [English]",
    ]

    relateds = dom.find("#id_related option")
    assert [item.text for item in relateds] == [
        "baguette [Français]",
        "egg [English]",
    ]

    categories = dom.find("#id_categories option")
    assert [item.text for item in categories] == [
        "ail [Français]",
        "garlic [English]",
    ]


def test_article_preview_modelchoice_change_labels(db):
    """
    Admin change form should have language names in model choices fields.
    """
    # Create new objects
    CategoryFactory(title="garlic", language="en")
    CategoryFactory(title="ail", language="fr")

    ArticleFactory(title="egg", language="en")
    obj_fr = ArticleFactory(title="baguette", language="fr")
    ArticleFactory(title="omelette", language="fr")

    # Build form and get its simple HTML representation to parse it
    f = ArticleAdminForm({"tags": []}, instance=obj_fr)
    content = f.as_p()
    dom = html_pyquery(content)

    originals = dom.find("#id_original option")
    assert [item.text for item in originals] == [
        f.fields["original"].empty_label,
        "egg [English]",
    ]

    relateds = dom.find("#id_related option")
    assert [item.text for item in relateds] == [
        "omelette [Français]",
    ]

    categories = dom.find("#id_categories option")
    assert [item.text for item in categories] == [
        "ail [Français]",
    ]
