import datetime
import json
from pathlib import Path

import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction

from bigtree import dict_to_tree, yield_tree
from freezegun import freeze_time

from lotus.exceptions import LanguageMismatchError
from lotus.factories import CategoryFactory, multilingual_category
from lotus.models import Category
from lotus.utils.imaging import DjangoSampleImageCrafter
from lotus.utils.tests import queryset_values
from lotus.utils.trees import (
    nested_list_to_flat_dict, queryset_to_flat_dict, compress_nested_tree,
)


def test_category_basic(db):
    """
    Basic model validation with required fields should not fail.
    """
    category = Category(
        title="Foo",
        slug="foo",
        depth=1,
        # Although valid it would probably not correct in practive since path is built
        # with a specific algorithm
        path="000C",
    )
    category.full_clean()
    category.save()

    assert 1 == Category.objects.filter(title="Foo").count()
    assert "Foo" == category.title


def test_category_required_fields(db):
    """
    Basic model validation with missing required fields should fail.
    """
    category = Category(language="")

    with pytest.raises(ValidationError) as excinfo:
        category.full_clean()

    assert excinfo.value.message_dict == {
        "title": ["This field cannot be blank."],
        "slug": ["This field cannot be blank."],
        "language": ["This field cannot be blank."],
        "depth": ["This field cannot be null."],
        "path": ["This field cannot be blank."],
    }


def test_category_creation(db):
    """
    Factory should correctly create a new object without any errors.
    """
    category = CategoryFactory(title="foo")
    assert category.title == "foo"


def test_category_constraints(db):
    """
    Category contraints should be respected.
    """
    # Base original objects
    bar = CategoryFactory(
        slug="bar",
    )
    CategoryFactory(
        slug="pong",
    )

    # We can have an identical slug for a different language.
    # Note than original is just a marker to define an object as a translation
    # of "original" relation object.
    CategoryFactory(
        slug="bar",
        language="fr",
        original=bar,
    )

    # But not an identical slug on the same language
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(
                slug="bar",
                language="en",
            )
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_category.slug, lotus_category.language"
        )

    # And only an unique language for the same original object is allowed since
    # there can't be two translations for the same language.
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(
                slug="zap",
                language="fr",
                original=bar,
            )
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_category.original_id, lotus_category.language"
        )

    # Combination of constraints (slug+lang & original+lang)
    with transaction.atomic():
        with pytest.raises(IntegrityError) as excinfo:
            CategoryFactory(
                slug="bar",
                language="fr",
                original=bar,
            )
        # This is the original+language constraint which raise first
        assert str(excinfo.value) == (
            "UNIQUE constraint failed: "
            "lotus_category.original_id, lotus_category.language"
        )


def test_category_move_into(db):
    """
    Model object method 'move_into' allows to insert an object as a child of another
    object but only for the same language.
    """
    picsou_category = CategoryFactory(
        title="Picsou",
        slug="picsou",
        language="en",
    )
    donald_category = CategoryFactory(
        title="Donald",
        slug="donald",
        language="en",
    )
    flairsou_category = CategoryFactory(
        title="Flairsou",
        slug="flairsou",
        language="fr",
    )

    # Insert a category with the same language
    donald_category.move_into(picsou_category)

    # Try to insert a category with a different language
    with pytest.raises(LanguageMismatchError) as excinfo:
        flairsou_category.move_into(picsou_category)

    assert str(excinfo.value) == (
        "Object with language 'fr' can not be moved as a child of another object "
        "with language 'en'"
    )

    # Proper children has been well saved
    assert [k.slug for k in picsou_category.get_children()] == ["donald"]


def test_multilingual_category(db):
    """
    Factory helper should create an original category with its required
    translations.
    """
    # Create a category with a FR and DE translations. Also try to create
    # Deutsch translations twice, but "multilingual_category" is safe on unique
    # language.
    created = multilingual_category(
        slug="recipe",
        langs=["fr", "de", "de"],
        contents={
            "fr": {
                "slug": "recette",
            }
        },
    )

    # Original slug is correct
    assert created["original"].slug == "recipe"

    # There is two related translations
    assert (len(created["translations"]) == 2) is True

    # Required translations have been create
    assert ("fr" in created["translations"]) is True
    assert ("de" in created["translations"]) is True

    # French translation have its own slug
    assert created["translations"]["fr"].slug == "recette"
    # Deutsch translation inherit from original slug
    assert created["translations"]["de"].slug == "recipe"


def test_category_get_by_lang(db):
    """
    Demonstrate how we can get categories for original language and
    translations.
    """
    created_foobar = CategoryFactory(slug="foobar")

    created_omelette = multilingual_category(
        slug="food",
        langs=["fr"],
    )

    created_cheese = multilingual_category(
        slug="recipe",
        langs=["fr", "de"],
        contents={
            "fr": {
                "slug": "recette",
            }
        },
    )

    # Get full total all languages mixed and without any filtering
    assert queryset_values(Category.objects.all()) == [
        {"slug": "foobar", "language": "en"},
        {"slug": "food", "language": "en"},
        {"slug": "food", "language": "fr"},
        {"slug": "recette", "language": "fr"},
        {"slug": "recipe", "language": "de"},
        {"slug": "recipe", "language": "en"},
    ]

    # Get available categories for a required language
    assert Category.objects.filter(language="en").count() == 3
    assert Category.objects.filter(language="fr").count() == 2
    assert Category.objects.filter(language="de").count() == 1

    # Get only originals
    results = Category.objects.filter(original__isnull=True)
    assert queryset_values(results) == [
        {"slug": "foobar", "language": "en"},
        {"slug": "food", "language": "en"},
        {"slug": "recipe", "language": "en"},
    ]

    # Get only translations
    results = Category.objects.filter(original__isnull=False)
    assert queryset_values(results) == [
        {"slug": "food", "language": "fr"},
        {"slug": "recette", "language": "fr"},
        {"slug": "recipe", "language": "de"},
    ]

    # Get translations from original
    assert created_foobar.category_set.all().count() == 0
    assert created_omelette["original"].category_set.all().count() == 1
    assert created_cheese["original"].category_set.all().count() == 2


def test_category_model_file_purge(db):
    """
    Category 'cover' field file should follow correct behaviors:

    * When object is deleted, its files should be delete from filesystem too;
    * When changing file from an object, its previous files (if any) should be
      deleted;
    """
    crafter = DjangoSampleImageCrafter()

    ping = CategoryFactory(
        cover=crafter.create(filename="machin.png")
    )
    pong = CategoryFactory(
        cover=crafter.create(filename="machin.png")
    )

    # Memorize some data to use after deletion
    ping_path = ping.cover.path
    pong_path = pong.cover.path

    # Delete object
    ping.delete()

    # File is deleted along its object
    assert Path(ping_path).exists() is False
    # Paranoiac mode: other existing similar filename (as uploaded) are conserved
    # since Django rename file with a unique hash if filename alread exist, they
    # should not be mistaken
    assert Path(pong_path).exists() is True

    # Change object file to a new one
    pong.cover = crafter.create(filename="new.png")
    pong.save()

    # During pre save signal, old file is removed from FS and new one is left
    # untouched
    assert Path(pong_path).exists() is False
    assert Path(pong.cover.path).exists() is True


def test_category_delete_tree(tests_settings, db):
    """
    Ensure that the category deletion cascade is respected when deleting a top level
    category, its descendants are removed also.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree_basic.json"
    )
    sample = json.loads(sample_path.read_text())

    Category.load_bulk(sample["tree"])

    # Loaded dump contains 4 categories and 3 are in the same branch (starting from
    # 'item-2')
    assert Category.objects.count() == 4

    # Deleting the 'item-2' deletes it along it descendants
    item_2 = Category.objects.get(slug="item-2")
    item_2.delete()
    assert Category.objects.count() == 1


def test_category_tree(tests_settings, db):
    """
    Check about treebear implementation behaviors during development.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree.json"
    )
    sample = json.loads(sample_path.read_text())

    Category.load_bulk(sample["tree"])

    # from lotus.utils.jsons import ExtendedJsonEncoder
    # print()
    # print("dump_bulk:")
    # print(json.dumps(Category.dump_bulk(), indent=4, cls=ExtendedJsonEncoder))
    # print()

    item_3 = Category.objects.get(slug="item-3")
    item_3_1 = Category.objects.get(slug="item-3-1")

    # 'get_tree' returns a queryset, not a tree structure
    assert [item.slug for item in Category.get_tree()] == [
        "item-1",
        "item-1-1",
        "item-2",
        "item-3",
        "item-3-1",
        "item-3-1-1",
        "item-3-1-2",
        "item-3-1-3",
        "item-3-1-4",
        "item-3-2",
    ]
    assert [item.slug for item in Category.get_tree().filter(language="fr")] == [
        "item-3-1-4",
    ]
    assert [item.slug for item in Category.get_tree(parent=item_3)] == [
        "item-3",
        "item-3-1",
        "item-3-1-1",
        "item-3-1-2",
        "item-3-1-3",
        "item-3-1-4",
        "item-3-2",
    ]
    assert [item.slug for item in Category.get_tree(parent=item_3_1)] == [
        "item-3-1",
        "item-3-1-1",
        "item-3-1-2",
        "item-3-1-3",
        "item-3-1-4",
    ]

    # Single object getters
    assert item_3.get_parent() is None
    assert item_3_1.get_parent().slug == item_3.slug

    # parenting getters return a queryset
    assert [item.slug for item in item_3.get_children()] == ["item-3-1", "item-3-2"]
    assert [item.slug for item in item_3.get_descendants().filter(language="en")] == [
        "item-3-1",
        "item-3-1-1",
        "item-3-1-2",
        "item-3-1-3",
        "item-3-2",
    ]

    # 'get_annotated_list_qs' allow to get annotated list from a queryset
    notated = [
        (obj.slug, data)
        for obj, data in Category.get_annotated_list_qs(
            item_3.get_descendants().filter(language="en")
        )
    ]
    assert notated == [
        ("item-3-1", {"open": True, "close": [], "level": 0}),
        ("item-3-1-1", {"open": True, "close": [], "level": 1}),
        ("item-3-1-2", {"open": False, "close": [], "level": 1}),
        ("item-3-1-3", {"open": False, "close": [0], "level": 1}),
        ("item-3-2", {"open": False, "close": [0], "level": 0})
    ]


def test_category_bulk_tree_render(tests_settings, db, django_assert_num_queries):
    """
    This is mostly a sample of how to convert treebeard node dump to bigtree nodes. The
    built trees should fit to the Category tree hierarchy.

    Note than node dumps is for all Categories, there is no way to filter it as a
    queryset.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree.json"
    )
    sample = json.loads(sample_path.read_text())

    Category.load_bulk(sample["tree"])

    # Build flat dict suitable for bigtree, this only perform a single queryset
    with django_assert_num_queries(1):
        nodes = nested_list_to_flat_dict(
            Category.dump_bulk(),
            nodes={
                ".": {"pk": 0, "title": ".", "language": None},
            },
            parent_path=".",
            depth=1,
        )

    # Check built dict
    dict_output = [
        "{pk}) {title} {path}".format(
            title=data["title"],
            path=path,
            pk=data["pk"],
        )
        for path, data in nodes.items()
    ]
    assert dict_output == [
        "0) . .",
        "2) Item 1 ./2",
        "3) Item 1.1 ./2/3",
        "1) Item 2 ./1",
        "4) Item 3 ./4",
        "5) Item 3.1 ./4/5",
        "6) Item 3.1.1 ./4/5/6",
        "9) Item 3.1.2 ./4/5/9",
        "7) Item 3.1.3 ./4/5/7",
        "8) Item 3.1.4 ./4/5/8",
        "10) Item 3.2 ./4/10",
    ]

    # Build tree with bigtree from built dict and check output
    tree_output = [
        "{branch}{stem}{title}".format(
            branch=branch,
            stem=stem,
            title=node.title,
        )
        for branch, stem, node in yield_tree(dict_to_tree(nodes), style="rounded")
    ]
    assert tree_output == [
        ".",
        "├── Item 1",
        "│   ╰── Item 1.1",
        "├── Item 2",
        "╰── Item 3",
        "    ├── Item 3.1",
        "    │   ├── Item 3.1.1",
        "    │   ├── Item 3.1.2",
        "    │   ├── Item 3.1.3",
        "    │   ╰── Item 3.1.4",
        "    ╰── Item 3.2",
    ]


def test_category_queryset_tree_render(tests_settings, db, django_assert_num_queries):
    """
    This is mostly a sample of how to convert Category tree queryset to bigtree nodes.
    The built trees should fit to the Category tree hierarchy.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree.json"
    )
    sample = json.loads(sample_path.read_text())

    Category.load_bulk(sample["tree"])

    with django_assert_num_queries(1):
        nodes = queryset_to_flat_dict(
            Category.get_tree(),
            nodes={
                ".": {"pk": 0, "title": ".", "language": None},
            },
            path_prefix="./",
        )

    # Check built dict
    dict_output = [
        "{pk}) {title} {path}".format(
            title=data["title"],
            path=path,
            pk=data["pk"],
        )
        for path, data in nodes.items()
    ]
    assert dict_output == [
        "0) . .",
        "2) Item 1 ./0001",
        "3) Item 1.1 ./0001/0001",
        "1) Item 2 ./0002",
        "4) Item 3 ./0003",
        "5) Item 3.1 ./0003/0001",
        "6) Item 3.1.1 ./0003/0001/0001",
        "9) Item 3.1.2 ./0003/0001/0002",
        "7) Item 3.1.3 ./0003/0001/0003",
        "8) Item 3.1.4 ./0003/0001/0004",
        "10) Item 3.2 ./0003/0002",
    ]

    # Build tree with bigtree from built dict and check output
    tree_output = [
        "{branch}{stem}{title}".format(
            branch=branch,
            stem=stem,
            title="{} [{}]".format(node.title, node.language),
        )
        for branch, stem, node in yield_tree(dict_to_tree(nodes), style="rounded")
    ]
    assert tree_output == [
        ". [None]",
        "├── Item 1 [en]",
        "│   ╰── Item 1.1 [en]",
        "├── Item 2 [en]",
        "╰── Item 3 [en]",
        "    ├── Item 3.1 [en]",
        "    │   ├── Item 3.1.1 [en]",
        "    │   ├── Item 3.1.2 [en]",
        "    │   ├── Item 3.1.3 [en]",
        "    │   ╰── Item 3.1.4 [fr]",
        "    ╰── Item 3.2 [en]",
    ]


@freeze_time("2012-10-15 10:00:00")
def test_category_get_nested_tree_basic(tests_settings, db, django_assert_num_queries):
    """
    Method 'get_nested_tree' without filter on a basic set just to demonstrate its
    output.
    """
    now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    sample_path = (
        tests_settings.fixtures_path / "category_tree_basic.json"
    )
    sample = json.loads(sample_path.read_text())

    Category.load_bulk(sample["tree"])

    with django_assert_num_queries(1):
        basic_tree = Category.get_nested_tree()

    assert basic_tree == [
        {
            "data": {
                "language": "en",
                "original": None,
                "modified": now,
                "title": "Item 1",
                "slug": "item-1",
                "lead": "",
                "description": "",
                "cover": ""
            },
            "id": 1
        },
        {
            "data": {
                "language": "en",
                "original": None,
                "modified": now,
                "title": "Item 2",
                "slug": "item-2",
                "lead": "",
                "description": "",
                "cover": ""
            },
            "id": 2,
            "children": [
                {
                    "data": {
                        "language": "en",
                        "original": None,
                        "modified": now,
                        "title": "Item 2.1",
                        "slug": "item-2-1",
                        "lead": "",
                        "description": "",
                        "cover": ""
                    },
                    "id": 3,
                    "children": [
                        {
                            "data": {
                                "language": "en",
                                "original": None,
                                "modified": now,
                                "title": "Item 2.1.1",
                                "slug": "item-2-1-1",
                                "lead": "",
                                "description": "",
                                "cover": ""
                            },
                            "id": 4
                        }
                    ]
                }
            ]
        }
    ]


def test_category_get_nested_tree_full(tests_settings, db, django_assert_num_queries):
    """
    Method 'get_nested_tree' without filter should return the full tree of categories.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree_with_different_languages.json"
    )
    sample = json.loads(sample_path.read_text())
    Category.load_bulk(sample["tree"])

    with django_assert_num_queries(1):
        full_tree = Category.get_nested_tree()
    assert compress_nested_tree(full_tree) == [
        "0) <.> [lang=None] [path=.]",
        "2) <Item 1> [lang=en] [path=./2]",
        "3) <Item 1.1> [lang=en] [path=./2/3]",
        "1) <Item 2> [lang=en] [path=./1]",
        "4) <Item 3> [lang=en] [path=./4]",
        "5) <Item 3.1> [lang=en] [path=./4/5]",
        "6) <Item 3.1.1> [lang=en] [path=./4/5/6]",
        "9) <Item 3.1.2> [lang=en] [path=./4/5/9]",
        "7) <Item 3.1.3> [lang=en] [path=./4/5/7]",
        "8) <Item 3.1.4> [lang=fr] [path=./4/5/8]",
        "10) <Item 3.2> [lang=en] [path=./4/10]",
        "11) <Item 4> [lang=fr] [path=./11]",
        "12) <Item 4.1> [lang=en] [path=./11/12]",
        "13) <Item 4.1.1> [lang=fr] [path=./11/12/13]"
    ]


def test_category_get_nested_tree_filtered(tests_settings, db,
                                           django_assert_num_queries):
    """
    Method 'get_nested_tree' with language argument should return a tree filter after
    language and resulting tree should omit all branch that are excluded from filter.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree_with_different_languages.json"
    )
    sample = json.loads(sample_path.read_text())
    Category.load_bulk(sample["tree"])

    with django_assert_num_queries(1):
        french_tree = Category.get_nested_tree(language="fr")
    assert compress_nested_tree(french_tree) == [
        "0) <.> [lang=None] [path=.]",
        "11) <Item 4> [lang=fr] [path=./11]",
    ]

    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(language="en")
    assert compress_nested_tree(english_tree) == [
        "0) <.> [lang=None] [path=.]",
        "2) <Item 1> [lang=en] [path=./2]",
        "3) <Item 1.1> [lang=en] [path=./2/3]",
        "1) <Item 2> [lang=en] [path=./1]",
        "4) <Item 3> [lang=en] [path=./4]",
        "5) <Item 3.1> [lang=en] [path=./4/5]",
        "6) <Item 3.1.1> [lang=en] [path=./4/5/6]",
        "9) <Item 3.1.2> [lang=en] [path=./4/5/9]",
        "7) <Item 3.1.3> [lang=en] [path=./4/5/7]",
        "10) <Item 3.2> [lang=en] [path=./4/10]"
    ]
