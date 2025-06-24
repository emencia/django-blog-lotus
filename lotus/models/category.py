from django.core import serializers
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import translate_url, reverse

from treebeard.mp_tree import MP_Node, get_result_class

from smart_media.mixins import SmartFormatMixin
from smart_media.modelfields import SmartMediaField
from smart_media.signals import auto_purge_files_on_change, auto_purge_files_on_delete

from ..choices import get_category_template_choices, get_category_template_default
from ..managers import CategoryManager
from ..exceptions import LanguageMismatchError
from .translated import Translated


class Category(SmartFormatMixin, MP_Node, Translated):
    """
    Category model.
    """
    original = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        help_text=_(
            "Mark this category as a translation of an original category."
        ),
    )
    """
    Optional original category when object is a translation.
    """

    modified = models.DateTimeField(
        _("modification date"),
        default=timezone.now,
        editable=False,
    )
    """
    Automatic modification date.
    """

    title = models.CharField(
        _("title"),
        blank=False,
        max_length=255,
        default="",
    )
    """
    Required unique title string.
    """

    slug = models.SlugField(
        _("slug"),
        max_length=255,
    )
    """
    Required unique slug string.
    """

    template = models.CharField(
        _("template"),
        blank=False,
        max_length=150,
        choices=get_category_template_choices(),
        default=get_category_template_default(),
    )
    """
    Optional custom template path string.
    """

    lead = models.TextField(
        _("lead"),
        blank=True,
        help_text=_(
            "Lead paragraph, commonly used for SEO purposes in page meta tags."
        ),
    )
    """
    Optional text lead.
    """

    description = models.TextField(
        _("description"),
        blank=True,
    )
    """
    Optional description string.
    """

    cover = SmartMediaField(
        verbose_name=_("cover image"),
        upload_to="lotus/category/cover/%y/%m",
        max_length=255,
        blank=True,
        default="",
    )
    """
    Optional cover image file.
    """

    cover_alt_text = models.CharField(
        _("cover alternative text"),
        blank=True,
        max_length=125,
        default="",
    )
    """
    Optional alternative text for cover image.
    """

    COMMON_ORDER_BY = ["title"]
    """
    List of field order commonly used in frontend view/api.
    """

    TREE_ORDER_BY = ["path", "title"]
    """
    List of field order to use with any tree queryset.
    """

    node_order_by = ["title"]
    """
    Treebeard attribute only used for ordering with position name when performing
    writing operation on categories.

    .. Warning::
        DO NOT CHANGE, it may corrupt tree for already saved data, however
        ``Category.fix_tree(fix_paths=True)`` should fix corruption.
    """

    objects = CategoryManager()

    class Meta:
        ordering = ["title"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "slug", "language"
                ],
                name="lotus_unique_cat_slug_lang"
            ),
            models.UniqueConstraint(
                fields=[
                    "original", "language"
                ],
                name="lotus_unique_cat_original_lang"
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return absolute URL to the category detail view.

        Returns:
            string: An URL.
        """
        return translate_url(
            reverse("lotus:category-detail", kwargs={"slug": self.slug}),
            self.language
        )

    def get_absolute_api_url(self):
        """
        Return absolute URL to the author detail viewset from API.

        Returns:
            string: An URL.
        """
        return reverse("lotus-api:category-detail", kwargs={"pk": self.id})

    def get_edit_url(self):
        """
        Return absolute URL to edit category from admin.

        Returns:
            string: An URL.
        """
        return reverse("admin:lotus_category_change", args=(self.id,))

    def get_subcategories(self):
        """
        Return category children, results are enforced on category language.

        Returns:
            queryset: List of children categories.
        """
        if not self.numchild:
            return []

        return self.get_children().filter(language=self.language).order_by("title")

    def get_cover_format(self):
        return self.media_format(self.cover)

    @classmethod
    def apply_tree_queryset_filter(cls, queryset, language=None, parent=None,
                                   current=None):
        """
        Apply lookups on a queryset to filter items.

        .. Warning::
            With some filter combinations this could return empty results.

        Arguments:
            queryset (Queryset): The queryset where to append filters.

        Keyword Arguments:
            cls (class object): The model class, typically ``Category``.
            language (string): Language code to use in queryset filter, every Category
                in different language will be excluded from results. If not given,
                all Category from mixed languages are returned.
            parent (Category): A category object used to start the tree. If not given,
                we assume than parent is the root of all categories meaning the whole
                tree will be returned.
            current (Category): The current category is used to find the tree branch
                to unfold. When given, only the nodes from the tree branch will be
                returned along the top level nodes (with the same depth than the
                parent) and children nodes that are not part of the branch are ignored.

        Returns:
            Queryset: The given queryset with possible filters. If no filter arguments
            are given, the queryset is returned unchanged.
        """
        if language:
            queryset = queryset.filter(language=language)

        if not current and not parent:
            return queryset

        if not current:
            return queryset.filter(path__startswith=parent.path)

        if not parent:
            top_depth = parent.depth if parent else 1
            return queryset.filter(
                models.Q(depth=top_depth) |
                models.Q(path__startswith=current.path[0:(Category.steplen * 1)])
            )

        branch_top_path = current.path[0:(Category.steplen * (parent.depth + 1))]
        return queryset.filter(
            models.Q(depth=parent.depth, path__startswith=parent.path) |
            models.Q(depth__gt=parent.depth, path__startswith=branch_top_path)
        )

    @classmethod
    def get_nested_tree(cls, parent=None, language=None, current=None, branch=True,
                        safe=True):
        """
        A convenient method to get a Category tree with language filtered or not.

        This was based on ``MP_Node.dump_bulk()`` method but opposed to it this
        method applies some filters on queryset.

        If language argument is set with "en" only the english objects will be returned
        from queryset, this means "Item 1", "Item 2" and "Item 3.1". However since
        "Item 3.1" is a child of "Item 3" that is excluded from language filter,
        "Items 3.1" won't be in resulting tree because its parent does not exist in
        results.

        The output is probably not suitable anymore with ``MP_Node.load_bulk()``
        because we keep/add some additional items to a node, opposed to the "dump_bulk"
        payload.

        .. Warning::
            With some filter combinations this could return an empty list.

        Arguments:
            cls (class object): The model class, typically ``Category``.
            language (string): Language code to use in queryset filter, every Category
                in different language will be excluded from results. If not given,
                all Category from mixed languages are returned.
            parent (Category): A category object used to start the tree. If not given,
                we assume than parent is the root of all categories meaning the whole
                tree will be returned.
            current (Category): Basically the current category is only used to mark a
                node as "active". But with ``branch`` argument enabled it will be used
                for the "branch unfolding" mode.
            branch (boolean): The current category will be used to find the tree branch
                to unfold. When this is true and ``current`` is given, only the nodes
                from the tree branch will be returned along the top level nodes (with
                the same depth than the parent) and children nodes that are not part of
                the branch are ignored.
            safe (boolean): Due to the fact we can exclude item from language filter,
                we can have KeyError exception when building tree. If this argument is
                true, there won't be any exception for this case and missing key will
                just be ignored. If false, any exception related to missing node key
                will be raised.

        Results:
            list: Recursive list of Category tree. Each item is dictionnary of node
            values and it will be something like this: ::

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
                    },
                    "id": 1,
                    "active": False,
                    "depth": 1,
                    "path": "0001",
                    "children": []
                }

            The ``children`` is only present if the node has children.

        """
        cls = get_result_class(cls)

        # Apply filters then the proper tree ordering
        queryset = cls.apply_tree_queryset_filter(
            cls._get_serializable_model().objects.all(),
            language=language,
            parent=parent,
            current=current if branch is True else None,
        )
        queryset = queryset.order_by(*cls.TREE_ORDER_BY)

        ret, lnk = [], {}
        pk_field = cls._meta.pk.attname

        for pyobj in serializers.serialize("python", queryset):
            # django's serializer stores the attributes in 'fields'
            fields = pyobj["fields"]
            path = fields["path"]
            depth = int(len(path) / cls.steplen)

            newobj = {"data": fields}

            # Move non data fields out of "data" item
            newobj[pk_field] = pyobj["pk"]
            newobj["path"] = fields["path"]
            newobj["depth"] = fields["depth"]

            # Add active state
            newobj["active"] = (current.id == pyobj["pk"]) if current else False

            # Clean useless fields from item payload
            del fields["numchild"]
            del fields["depth"]
            del fields["path"]

            # Remove id from data fields
            if pk_field in fields:
                del fields[pk_field]

            if (
                (not parent and depth == 1) or
                (parent and len(path) == len(parent.path))
            ):
                ret.append(newobj)
            else:
                parentpath = cls._get_basepath(path, depth - 1)

                # Ensure unknow path relation don't raise KeyError in case of queryset
                # filters that drops some nodes linked to granted nodes (mostly with
                # language filter)
                # CAUTION: If queryset is not ordered first on 'path' this will drop
                # some legitimate items
                if safe and parentpath not in lnk:
                    continue

                parentobj = lnk[parentpath]

                if "children" not in parentobj:
                    parentobj["children"] = []

                parentobj["children"].append(newobj)

            lnk[path] = newobj

        return ret

    def move_into(self, parent):
        """
        Move object as a child of given parent.

        This is a shortcut around MP_Node.move() method but with positionning forced
        on 'sorted child' technic because it is the only one that fit to Lotus needs.

        You should never try to manually set a Category as a child of a parent
        Category because it will probably not correctly manage the node path rewriting.

        Raises:
            LanguageMismatchError: If both object language and parent language
                are differents.

        Arguments:
            parent (Category): A category object to define as the parent.
        """
        # Enforce language validation before performing tree insertion
        if parent.language != self.language:
            msg = (
                "Object with language '{current_lang}' can not be moved as a child of "
                "another object with language '{parent_lang}'"
            )
            raise LanguageMismatchError(msg.format(
                parent_lang=parent.language,
                current_lang=self.language,
            ))

        self.move(parent, pos="sorted-child")

    def save(self, *args, **kwargs):
        # Auto update 'modified' value on each save
        self.modified = timezone.now()

        super().save(*args, **kwargs)


# Connect some signals
post_delete.connect(
    auto_purge_files_on_delete(["cover"]),
    dispatch_uid="category_cover_on_delete",
    sender=Category,
    weak=False,
)
pre_save.connect(
    auto_purge_files_on_change(["cover"]),
    dispatch_uid="category_cover_on_change",
    sender=Category,
    weak=False,
)
