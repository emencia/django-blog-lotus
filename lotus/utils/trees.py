
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
