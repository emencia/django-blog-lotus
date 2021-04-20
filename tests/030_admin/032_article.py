import os

from django.core.files.uploadedfile import SimpleUploadedFile

from lotus.factories import ArticleFactory, CategoryFactory
from lotus.forms import ArticleAdminForm
from lotus.models import Article
from lotus.utils.tests import (
    DUMMY_GIF_BYTES, html_pyquery, compact_form_errors, build_post_data_from_object,
    get_admin_add_url, get_admin_change_url, get_admin_list_url,
)


def test_article_admin_add(db, admin_client):
    """
    Article model admin add form view should not raise error on GET request.
    """
    url = get_admin_add_url(Article)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_list(db, admin_client):
    """
    Article model admin list view should not raise error on GET request.
    """
    url = get_admin_list_url(Article)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_detail(db, admin_client):
    """
    Article model admin detail view should not raise error on GET request.
    """
    obj = ArticleFactory()

    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200


def test_article_admin_change_form(db, admin_client):
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
    )

    # Fields we don't want to post anything
    ignored_fields = ["id", "relations", "article"]

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
    assert os.path.exists(obj.cover.path) is True
    assert os.path.exists(obj.image.path) is True


def test_article_admin_original_choices(db, admin_client):
    """
    Choices should be limited to some constraints:

    * 'original' field should not list items in same language and not the
      article itself;
    * 'related' field should not list items in different language and not the
      article itself;
    * 'categories' field should not list items in different language;
    """
    # Create new object to check
    obj = ArticleFactory(language="en")
    # Create some objects in same language
    fillers_en = [
        ArticleFactory(language="en"),
        ArticleFactory(language="en"),
    ]
    # Create some other objects in various other languages, these are the only
    # elligible articles for original field choices
    fillers_langs = [
        ArticleFactory(language="fr"),
        ArticleFactory(language="fr"),
        ArticleFactory(language="de"),
    ]
    # Create some categories
    cat_en = CategoryFactory(language="en")
    CategoryFactory(language="fr")

    # Get the obj detail page
    url = get_admin_change_url(obj)
    response = admin_client.get(url)

    assert response.status_code == 200

    dom = html_pyquery(response)

    # Get available 'original' choice ids from their values
    options = dom.find("#id_original option")
    option_ids = [int(item.get("value")) for item in options if item.get("value")]

    assert sorted(option_ids) == sorted([item.id for item in fillers_langs])

    # Get available 'related' choice ids from their values
    options = dom.find("#id_related option")
    option_ids = [int(item.get("value")) for item in options if item.get("value")]

    assert sorted(option_ids) == sorted([item.id for item in fillers_en])

    # Get available 'categories' choice ids from their values
    options = dom.find("#id_categories option")
    option_ids = [cat_en.id]


def test_article_admin_original_validation(db, admin_client):
    """
    Changing language should not allow to trick constraint on original relation
    which must be in different language.
    """
    # Create new object without a cover file
    obj_a = ArticleFactory(language="fr")
    obj_b = ArticleFactory(language="en")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories",
    ]
    data = build_post_data_from_object(Article, obj_a, ignore=ignore)

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


def test_article_admin_original_add_validation(db, admin_client):
    """
    Just add an original in different language should work.
    """
    # Create new objects
    obj_fr = ArticleFactory(language="fr")
    obj_en = ArticleFactory(language="en")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories",
    ]
    data = build_post_data_from_object(Article, obj_fr, ignore=ignore)

    data["original"] = obj_en

    f = ArticleAdminForm(data, instance=obj_fr)
    # No validation errors
    assert f.is_valid() is True
    assert compact_form_errors(f) == {}
    assert obj_fr.original.language != obj_fr.language

    obj_fr = f.save()


def test_article_admin_original_change_validation(db, admin_client):
    """
    Changing language should not allow to trick constraint on original relation
    which must be in different language.
    """
    # Create new objects
    obj_en = ArticleFactory(language="en")
    obj_fr = ArticleFactory(language="fr", original=obj_en)

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories",
    ]
    data = build_post_data_from_object(Article, obj_fr, ignore=ignore)

    # Trying to switch language to 'EN' should not allow to keep the original
    # relation on 'obj_en' in 'EN' language
    data["language"] = "en"
    f = ArticleAdminForm(data, instance=obj_fr)

    assert f.is_valid() is False
    assert compact_form_errors(f) == {
        "language": ["invalid"],
        "original": ["invalid"],
    }


def test_article_admin_related_create_validation(db, admin_client):
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
        "id", "relations", "article", "authors", "related", "categories",
    ]
    data = build_post_data_from_object(Article, build_fr, ignore=ignore)

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


def test_article_admin_related_change_validation(db, admin_client):
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
        "id", "relations", "article", "authors", "related", "categories",
    ]
    data = build_post_data_from_object(Article, obj_fr, ignore=ignore)

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


def test_article_admin_category_create_validation(db, admin_client):
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
        "id", "relations", "article", "authors", "related", "categories",
    ]
    data = build_post_data_from_object(Article, build_fr, ignore=ignore)

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


def test_article_admin_category_change_validation(db, admin_client):
    """
    Admin change form should not allow to set category with a different
    language.
    """
    cat_en = CategoryFactory(language="en")
    cat_fr = CategoryFactory(language="fr")
    obj_fr = ArticleFactory(language="fr")

    # Build initial POST data
    ignore = [
        "id", "relations", "article", "authors", "related", "categories",
    ]
    data = build_post_data_from_object(Article, obj_fr, ignore=ignore)

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
