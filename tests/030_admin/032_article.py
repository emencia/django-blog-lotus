from pathlib import Path
import datetime

from freezegun import freeze_time

# Try to use the builtin zoneinfo available since Python 3.9
try:
    from zoneinfo import ZoneInfo
# Django 4.x install the backports for Python 3.8
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from lotus.choices import STATUS_DRAFT
from lotus.factories import multilingual_article, ArticleFactory, CategoryFactory
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


@freeze_time("2012-10-15 10:00:00")
def test_article_admin_list_is_published(db, admin_client):
    """
    Article model admin list view should have the right content for item column
    "is_published" depending item is published or not (following publication criterias).
    """
    # Date references
    utc = ZoneInfo("UTC")
    today = datetime.datetime(2012, 10, 15, 1, 00).replace(tzinfo=utc)
    past_hour = datetime.datetime(2012, 10, 15, 9, 00).replace(tzinfo=utc)
    next_hour = datetime.datetime(2012, 10, 15, 11, 00).replace(tzinfo=utc)

    draft = ArticleFactory(
        title="draft",
        publish_date=today.date(),
        publish_time=today.time(),
        status=STATUS_DRAFT,
    )
    basic = ArticleFactory(
        title="basic published",
        publish_date=today.date(),
        publish_time=today.time(),
    )
    published_notyet = ArticleFactory(
        title="not yet published",
        publish_date=next_hour.date(),
        publish_time=next_hour.time(),
    )
    published_passed = ArticleFactory(
        title="published but ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
    )
    published_private_passed = ArticleFactory(
        title="published, private and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        private=True,
    )
    draft_passed = ArticleFactory(
        title="draft and ended one hour ago",
        publish_date=today.date(),
        publish_time=today.time(),
        publish_end=past_hour,
        status=STATUS_DRAFT,
    )

    # Collect published and not published id apart
    expected_published_ids = [basic.id]
    expected_unpublished_ids = [
        draft.id,
        published_notyet.id,
        published_passed.id,
        published_private_passed.id,
        draft_passed.id
    ]

    # Get list view response
    url = get_admin_list_url(Article)
    response = admin_client.get(url)
    assert response.status_code == 200

    # Parse table rows to get article ids and publication state
    resulting_published_ids = []
    resulting_unpublished_ids = []
    dom = html_pyquery(response)
    for row in dom.find("#result_list tbody tr"):
        article_id = row.cssselect(
            "td.action-checkbox input.action-select"
        )[0].get("value")
        article_published = row.cssselect("td.field-is_published img")[0].get("alt")
        if article_published == "True":
            resulting_published_ids.append(int(article_id))
        else:
            resulting_unpublished_ids.append(int(article_id))

    assert sorted(resulting_published_ids) == sorted(expected_published_ids)
    assert sorted(resulting_unpublished_ids) == sorted(expected_unpublished_ids)


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
        fill_tags=True,
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
        if name in ("categories", "authors", "related", "tags"):
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
    assert Path(obj.cover.path).exists() is True
    assert Path(obj.image.path).exists() is True


def test_article_admin_original_choices(db, admin_client):
    """
    Choices should be limited to some constraints:

    * 'original' field should not list items in same language, not the
      article itself and only original articles;
    * 'related' field should not list items in different language and not the
      article itself;
    * 'categories' field should not list items in different language;
    """
    # Create new object to check
    obj = ArticleFactory(language="en")
    # Create new object as a translation
    ArticleFactory(language="fr", original=obj)

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
        "id", "relations", "article", "authors", "related", "categories", "tags",
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
        "id", "relations", "article", "authors", "related", "categories", "tags",
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


def test_article_preview_modelchoice_create_labels(db, admin_client):
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


def test_article_preview_modelchoice_change_labels(db, admin_client):
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
    f = ArticleAdminForm({}, instance=obj_fr)
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


def test_article_admin_translate_button_empty(db, admin_client):
    """
    Translate button should not be in detail if there is no available language for
    translation and finally the translate page should not contain form since there is
    language available.
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
        "admin:lotus_article_translate_original",
        args=(created_cheese["original"].id,),
    )
    response = admin_client.get(url)
    assert response.status_code == 200

    dom = html_pyquery(response)
    forms = dom.find("#lotus-translate-original-form")
    assert len(forms) == 0


def test_article_admin_translate_button_expected(db, admin_client):
    """
    Translate button should be in detail page with the right URL and lead to the
    "Translate" form with the right available languages.
    """
    ping = CategoryFactory(slug="ping")

    # Create meat articles with unpublished DE translation
    created_beef = multilingual_article(
        title="Beef",
        slug="beef",
        langs=["de"],
        fill_categories=[ping],
        contents={
            "de": {
                "title": "Rindfleisch",
                "slug": "rindfleisch",
                "fill_categories": [ping],
                "status": STATUS_DRAFT,
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
