import datetime
import json

from freezegun import freeze_time

from lotus.models import Category
from lotus.utils.trees import compress_nested_tree


def test_category_tree(tests_settings, db):
    """
    Checks about treebeard API behaviors.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree.json"
    )
    sample = json.loads(sample_path.read_text())

    Category.load_bulk(sample["tree"])

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


def test_category_apply_tree_queryset_filter(tests_settings, db,
                                             django_assert_num_queries):
    """
    Class method "apply_tree_queryset_filter" should correctly apply filters on
    queryset to return tree items.
    """
    # Internal helper function to format results
    def format_results(node):
        indent = "   " * (node.depth - 1)
        return indent + "└─ " + node.title

    # Get and load fixture datas
    sample_path = (
        tests_settings.fixtures_path / "category_tree_with_different_languages.json"
    )
    sample = json.loads(sample_path.read_text())
    Category.load_bulk(sample["tree"])

    # Without any language and additional filters
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language=None,
        parent=None,
        current=None,
    )
    with django_assert_num_queries(1):
        assert [format_results(item) for item in tree] == [
            "└─ Item 1",
            "   └─ Item 1.1",
            "└─ Item 2",
            "└─ Item 3",
            "   └─ Item 3.1",
            "      └─ Item 3.1.1",
            "      └─ Item 3.1.2",
            "      └─ Item 3.1.3",
            "      └─ Item 3.1.4",
            "   └─ Item 3.2",
            "└─ Item 4",
            "   └─ Item 4.1",
            "      └─ Item 4.1.1",
        ]

    # Without any additional filters
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language="en",
        parent=None,
        current=None,
    )
    assert [format_results(item) for item in tree] == [
        "└─ Item 1",
        "   └─ Item 1.1",
        "└─ Item 2",
        "└─ Item 3",
        "   └─ Item 3.1",
        "      └─ Item 3.1.1",
        "      └─ Item 3.1.2",
        "      └─ Item 3.1.3",
        "   └─ Item 3.2",
        # This one would be ignored from 'get_nested_tree' because it have an ascendant
        # with "fr" language
        "   └─ Item 4.1",
    ]

    # With parent filter on top level category
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language="en",
        parent=Category.objects.get(title="Item 3"),
        current=None,
    )
    assert [format_results(item) for item in tree] == [
        "└─ Item 3",
        "   └─ Item 3.1",
        "      └─ Item 3.1.1",
        "      └─ Item 3.1.2",
        "      └─ Item 3.1.3",
        "   └─ Item 3.2",
    ]

    # With non root parent filter
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language="en",
        parent=Category.objects.get(title="Item 3.1"),
        current=None,
    )
    assert [format_results(item) for item in tree] == [
        "   └─ Item 3.1",
        "      └─ Item 3.1.1",
        "      └─ Item 3.1.2",
        "      └─ Item 3.1.3",
    ]

    # Without any language and with current filter
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language=None,
        parent=None,
        current=Category.objects.get(title="Item 3.1"),
    )
    assert [format_results(item) for item in tree] == [
        "└─ Item 1",
        "└─ Item 2",
        "└─ Item 3",
        "   └─ Item 3.1",
        "      └─ Item 3.1.1",
        "      └─ Item 3.1.2",
        "      └─ Item 3.1.3",
        "      └─ Item 3.1.4",
        "   └─ Item 3.2",
        "└─ Item 4",
    ]

    # With current filter
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language="en",
        parent=None,
        current=Category.objects.get(title="Item 3.1.2"),
    )
    assert [format_results(item) for item in tree] == [
        "└─ Item 1",
        "└─ Item 2",
        "└─ Item 3",
        "   └─ Item 3.1",
        "      └─ Item 3.1.1",
        "      └─ Item 3.1.2",
        "      └─ Item 3.1.3",
        "   └─ Item 3.2",
    ]

    # With parent and current filters
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language="en",
        parent=Category.objects.get(title="Item 3"),
        current=Category.objects.get(title="Item 3.1.2"),
    )
    assert [format_results(item) for item in tree] == [
        "└─ Item 3",
        "   └─ Item 3.1",
        "      └─ Item 3.1.1",
        "      └─ Item 3.1.2",
        "      └─ Item 3.1.3",
    ]

    # Without language with parent and current filters
    tree = Category.apply_tree_queryset_filter(
        Category.objects.all(),
        language=None,
        parent=Category.objects.get(title="Item 3"),
        current=Category.objects.get(title="Item 3.1.2"),
    )
    # print("\n".join([format_results(item) for item in tree]))
    assert [format_results(item) for item in tree] == [
        "└─ Item 3",
        "   └─ Item 3.1",
        "      └─ Item 3.1.1",
        "      └─ Item 3.1.2",
        "      └─ Item 3.1.3",
        "      └─ Item 3.1.4",
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
                "cover": "",
                "cover_alt_text": "",
            },
            "id": 1,
            "depth": 1,
            "path": "0001",
            "active": False,
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
                "cover": "",
                "cover_alt_text": "",
            },
            "id": 2,
            "depth": 1,
            "path": "0002",
            "active": False,
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
                        "cover": "",
                        "cover_alt_text": "",
                    },
                    "id": 3,
                    "depth": 2,
                    "path": "00020001",
                    "active": False,
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
                                "cover": "",
                                "cover_alt_text": "",
                            },
                            "id": 4,
                            "depth": 3,
                            "path": "000200010001",
                            "active": False,
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
    Method 'get_nested_tree' should apply filters as given from arguments and then
    return a correct tree list.
    """
    sample_path = (
        tests_settings.fixtures_path / "category_tree_with_different_languages.json"
    )
    sample = json.loads(sample_path.read_text())
    Category.load_bulk(sample["tree"])

    # Get some objects from created tree
    item_1_1 = Category.objects.get(title="Item 1.1")
    item_3 = Category.objects.get(title="Item 3")
    item_3_1 = Category.objects.get(title="Item 3.1")
    item_3_1_2 = Category.objects.get(title="Item 3.1.2")
    item_4 = Category.objects.get(title="Item 4")
    item_4_1 = Category.objects.get(title="Item 4.1")

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

    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(
            language="fr",
            parent=item_4,
        )
    assert compress_nested_tree(english_tree) == [
        "0) <.> [lang=None] [path=.]",
        "11) <Item 4> [lang=fr] [path=./11]",
    ]

    # With only 'current', there is no change on results (except the active attribute)
    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(
            language="en",
            current=item_3_1,
            branch=False,
        )
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

    # With only 'current', there is no change on results (except the active attribute)
    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(
            language="en",
            current=item_1_1,
            branch=True,
        )
    assert compress_nested_tree(english_tree) == [
        "0) <.> [lang=None] [path=.]",
        "2) <Item 1> [lang=en] [path=./2]",
        "3) <Item 1.1> [lang=en] [path=./2/3]",
        "1) <Item 2> [lang=en] [path=./1]",
        "4) <Item 3> [lang=en] [path=./4]",
    ]

    # The same as previous but with a different current category
    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(
            language="en",
            current=item_3_1_2,
            branch=True,
        )
    assert compress_nested_tree(english_tree) == [
        "0) <.> [lang=None] [path=.]",
        "2) <Item 1> [lang=en] [path=./2]",
        "1) <Item 2> [lang=en] [path=./1]",
        "4) <Item 3> [lang=en] [path=./4]",
        "5) <Item 3.1> [lang=en] [path=./4/5]",
        "6) <Item 3.1.1> [lang=en] [path=./4/5/6]",
        "9) <Item 3.1.2> [lang=en] [path=./4/5/9]",
        "7) <Item 3.1.3> [lang=en] [path=./4/5/7]",
        "10) <Item 3.2> [lang=en] [path=./4/10]"
    ]

    # With 'branch' enabled and current on a filtered out category (because of language)
    # this does not raise error but the branch is not available since it starts on
    # non english language
    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(
            language="en",
            current=item_4_1,
            branch=True,
        )
    assert compress_nested_tree(english_tree) == [
        "0) <.> [lang=None] [path=.]",
        "2) <Item 1> [lang=en] [path=./2]",
        "1) <Item 2> [lang=en] [path=./1]",
        "4) <Item 3> [lang=en] [path=./4]",
    ]

    # With 'branch' enabled, current category and a parent
    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(
            language="en",
            parent=item_3,
            current=item_3_1_2,
            branch=True,
        )
    assert compress_nested_tree(english_tree) == [
        "0) <.> [lang=None] [path=.]",
        "4) <Item 3> [lang=en] [path=./4]",
        "5) <Item 3.1> [lang=en] [path=./4/5]",
        "6) <Item 3.1.1> [lang=en] [path=./4/5/6]",
        "9) <Item 3.1.2> [lang=en] [path=./4/5/9]",
        "7) <Item 3.1.3> [lang=en] [path=./4/5/7]",
    ]

    # With 'branch' enabled, a parent in non english and a current out of parent
    with django_assert_num_queries(1):
        english_tree = Category.get_nested_tree(
            language="en",
            parent=item_4,
            current=item_3_1_2,
            branch=True,
        )
    assert compress_nested_tree(english_tree) == [
        "0) <.> [lang=None] [path=.]",
    ]
