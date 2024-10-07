import textwrap

from django.core import serializers

from bigtree import dict_to_tree, yield_tree


def nested_list_to_flat_dict(items, nodes=None, parent_path=None, depth=None):
    """
    Build a flat dictionnary from a Category tree nested list.

    Arguments:
        items (list): Nested list of categories in the same format produced by
            ``Category.dump_bulk()``. The function will compute the current level
            items before recursively proceed to the items children if any.

    Keyword arguments:
        nodes (dict): Initial tree node dictionnary where to add node items, it will
            start as an empty dict if not given.
        parent_path (string): The last parent node path (like ``root/foo/bar``) to use
            to start the path of current items.
        depth (integer): Depth level for current items from ``items``.

    Returns:
        dict: Flat dictionnary of tree nodes. Each item
        key is the node path and item value is a dict of object model attributes
        (primary key id, title, etc.. plus the node depth and path).
    """
    depth = depth or 0
    nodes = {} if nodes is None else nodes.copy()
    parent_path = "" if parent_path is None else parent_path

    for node in items:
        if parent_path:
            path = parent_path + "/" + str(node["id"])
        else:
            path = str(node["id"])

        node["data"].update({"pk": node["id"], "depth": depth, "path": path})
        nodes[path] = node["data"]

        # Follow recursive children
        if "children" in node:
            nodes.update(
                nested_list_to_flat_dict(
                    node["children"],
                    nodes=nodes,
                    parent_path=path,
                    depth=depth + 1,
                )
            )

    return nodes


def queryset_to_flat_dict(queryset, nodes=None, path_prefix=None):
    """
    Build a flat dictionnary from a queryset for Bigtree library.

    Arguments:
        queryset (Queryset): Queryset on a model which implement treebeard ``MP_Node``.

    Keyword arguments:
        nodes (dict): Initial tree node dictionnary where to add node items, it will
            start as an empty dict if not given.
        path_prefix (string): Prefix to add to every paths, commonly used to root all
            node paths to a node that comes from the ones from initial ``nodes`` value.
            The prefix must always ends with path divider character ``/``.

    Returns:
        dict: Dictionnary of tree nodes suitable to 'bigtree.dict_to_tree()'. Each item
        key is the node path and item value is a dict of object model attributes
        (primary key id, title, etc..).
    """
    nodes = {} if nodes is None else nodes.copy()
    path_prefix = path_prefix or ""

    for item in serializers.serialize("python", queryset):
        # Convert treebeard path to bigtree path
        path = path_prefix + "/".join(textwrap.wrap(item["fields"]["path"], 4))
        # Build data with added item primary key and some treebeard attributes removed
        nodes[path] = {
            k: v
            for k, v in item["fields"].items()
            if k not in ["path", "numchild"]
        }
        nodes[path]["pk"] = item["pk"]

    return nodes


def tree_all_category(model):
    """
    Helper to quickly display a plain text tree of all nodes from a Model which inherit
    from a treebeard node model.

    .. Warning::
        This uses some Bigtree library functions.

    Returns:
        list: List of tree lines. Commonly to display it you will join lines with
        ``\n`` character.
    """
    nodes = nested_list_to_flat_dict(
        model.dump_bulk(),
        nodes={
            ".": {"pk": 0, "title": ".", "language": "-", "path": "root"},
        },
        parent_path=".",
        depth=1,
    )

    return [
        "{branch}{stem}{title} [{lang}] : [{path}]".format(
            branch=branch,
            stem=stem,
            path=node.path,
            title=node.title,
            lang=node.language,
        )
        for branch, stem, node in yield_tree(dict_to_tree(nodes), style="rounded")
    ]


def compress_nested_tree(tree, depth=None):
    """
    Helper to compress a nested tree to a list of items.

    .. Note::
        This will only works with a tree made for model with a ``title`` attribute, a
        ``language`` attribute and inheriter of ``MP_Node``.

    Arguments:
        tree (list): Tree nodes as nested list in the same format returned from
            ``MP_Node.dump_bulk`` which look alike: ::

                []

    Returns:
        list: A list of item formatted to a string containing object id, title,
        language and node path like: ::

            [
                "0) . (None) .",
                "1) <Item 1> [lang=en] [path=./1]",
                "2) <Item 1.1> [lang=en] [path=./1/2]",
                "3) <Item 2> [lang=fr] [path=./3]",
            ]

        The first item is an artefact to gather every nodes for when you don't have an
        unique root. Since it is not a real node item you may remove it if needed.
    """
    nodes = nested_list_to_flat_dict(
        tree,
        nodes={
            ".": {"pk": 0, "title": ".", "language": None},
        },
        parent_path=".",
        depth=depth,
    )

    return [
        "{pk}) <{title}> [lang={lang}] [path={path}]".format(
            path=path,
            title=data["title"],
            lang=data["language"],
            pk=data["pk"],
        )
        for path, data in nodes.items()
    ]
