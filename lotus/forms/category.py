from django import forms
from django.conf import settings
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from treebeard.forms import MoveNodeForm, movenodeform_factory

from ..models import Category
from ..formfields import TranslatedModelChoiceField


# Use the right field depending 'ckeditor_uploader' app is enabled or not
if "ckeditor_uploader" in settings.INSTALLED_APPS:
    from ckeditor_uploader.widgets import CKEditorUploadingWidget as CKEditorWidget
else:
    from ckeditor.widgets import CKEditorWidget


# Use the specific CKEditor config if defined
CONFIG_NAME = "lotus"
CKEDITOR_CONFIG = getattr(settings, "CKEDITOR_CONFIGS", {})
if CONFIG_NAME not in CKEDITOR_CONFIG:
    CONFIG_NAME = "default"


class CategoryNodeAbstractForm(MoveNodeForm):
    """
    Abstract node form for Category model.

    This abstract only cares about the form stuff related to treebeard, everything else
    will live in the concrete form class.

    According to treebeard documentation it is recommended to not directly inherit from
    MoveNodeForm and prefer to use ``movenodeform_factory`` to build the proper form
    class to extend.
    """
    PARENT_EMPTY_LABEL = _("-- Root --")

    @staticmethod
    def mk_indent(level):
        if level == 1:
            return ""

        if level == 2:
            return "└── "

        return ("&nbsp;&nbsp;&nbsp;&nbsp;" * (level - 1)) + "└── "

    @classmethod
    def add_subtree(cls, for_node, node, options, excluded=None):
        """
        Build options tree with categories that are not excluded.

        TODO: Right tree order should be applied on queryset
        """
        excluded = excluded or []

        if cls.is_loop_safe(for_node, node):
            for item, data in node.get_annotated_list(node):
                # Ignore excluded items
                if item.pk in excluded:
                    continue

                name = "{indent}{name} [{lang}]".format(
                    indent=cls.mk_indent(item.get_depth()),
                    name=escape(item),
                    lang=item.get_language_display(),
                )
                options.append(
                    (
                        item.pk,
                        mark_safe(name),
                    )
                )

    @classmethod
    def mk_dropdown_tree(cls, model, for_node=None):
        """
        Build the choice list for available Category nodes.

        The currently edited Category, if any, will be excluded along its descendants.

        TODO: Right tree order should be applied on queryset
        """
        descendants = []
        if for_node:
            descendants = list(
                for_node.get_descendants().values_list("id", flat=True)
            ) + [for_node.pk]

        options = [(None, cls.PARENT_EMPTY_LABEL)]
        for node in model.get_root_nodes():
            cls.add_subtree(for_node, node, options, excluded=descendants)
        return options


CategoryNodeForm = movenodeform_factory(Category, form=CategoryNodeAbstractForm)
"""
Build the Form class with proper Metas and stuff calibrated by treebeard, this the one
to inherit and extend.
"""


class CategoryAdminForm(CategoryNodeForm):
    """
    Category form for admin.

    .. Note::
        Form is customized to manage treebeard fields for our constraint requirements.
    """
    def __init__(self, *args, **kwargs):
        if "initial" not in kwargs:
            kwargs["initial"] = {}

        # We only support the 'sorted child' appending. So here we force its initial
        # field value and finally the field won't be displayed so it will always use
        # this value
        kwargs["initial"].update({"_position": "sorted-child"})

        super().__init__(*args, **kwargs)

        # Rename treebeard "node id" attribute label for something more comprehensive
        self.fields["_ref_node_id"].label = _("Parent")
        # Make position hidden since we only support the sorted child appending
        self.fields["_position"].widget = forms.HiddenInput()

        # Apply choice limit on 'original' field queryset to avoid selecting
        # itself or object with the same language
        self.fields["original"] = TranslatedModelChoiceField(
            queryset=self.get_original_relation_queryset(),
            required=False,
            blank=True,
        )

    def get_original_relation_queryset(self):
        """
        Get available categories queryset for original field selection.

        Returns:
            Queryset: Queryset of available category. Basically only the original
            categories are available. And in addition when form is in edition mode,
            queryset is filtered with some constraints to avoid selecting the category
            itself, a translation or object with the same language.
        """
        base_queryset = Category.objects.filter(
            original__isnull=True
        ).order_by(*Category.COMMON_ORDER_BY)

        # Model choice querysets for creation form get all objects since there is no
        # data yet to constraint
        if not self.instance.pk:
            return base_queryset

        return base_queryset.exclude(
            models.Q(id=self.instance.id) |
            models.Q(language=self.instance.language)
        )

    def clean(self):
        """
        Add custom global input cleaner validations.

        WARNING: It seems it is possible to define an "original" category even if the
        current category itself has translations which should make it as the original
        for these translations, so the current category could not be a translation.
        This is the same behavior with articles. Issue #79.
        """
        cleaned_data = super().clean()
        language = cleaned_data.get("language")
        original = cleaned_data.get("original")
        ref_node_id = cleaned_data.get("_ref_node_id") or None

        # Cast possible selected parend node choice as a Category object
        parent = None
        if ref_node_id:
            parent = Category.objects.get(pk=int(ref_node_id))

        if parent:
            # Parent must have the same language than current category
            if parent.language != language:
                self.add_error(
                    "_ref_node_id",
                    forms.ValidationError(
                        _(
                            "You can't have a parent category with a different "
                            "language."
                        ),
                        code="invalid",
                    ),
                )
                self.add_error(
                    "language",
                    forms.ValidationError(
                        _(
                            "You can't have a language different from the parent "
                            "category one."
                        ),
                        code="invalid",
                    ),
                )

        # Original must not be in the same language than current category
        if original and original.language == language:
            self.add_error(
                "language",
                forms.ValidationError(
                    _(
                        "You can't have a language identical to the original "
                        "relation."
                    ),
                    code="invalid",
                ),
            )
            self.add_error(
                "original",
                forms.ValidationError(
                    _(
                        "You can't have an original relation in the same language."
                    ),
                    code="invalid",
                ),
            )

        # For edition mode
        if self.instance.pk:
            # Check if an article has a translation, in this case it can not
            # select an original object since it is already an original.
            if original and Category.objects.filter(original_id=self.instance.pk):
                self.add_error(
                    "original",
                    forms.ValidationError(
                        _(
                            "This category already have a translation so it can not be "
                            "a translation itself."
                        ),
                        code="invalid-original",
                    ),
                )

            # Block save if language has been changed to another but the category still
            # have articles in previous language
            if self.instance.articles.exclude(language=language).count() > 0:
                self.add_error(
                    "language",
                    forms.ValidationError(
                        _(
                            "Some articles in different language relate to this "
                            "category, you can't change language until those articles "
                            "are not related anymore."
                        ),
                        code="invalid-language",
                    ),
                )

            # Current category can not change language if it have descendants
            # since they are in different language.
            if self.instance.get_descendants().exclude(language=language).count() > 0:
                self.add_error(
                    "language",
                    forms.ValidationError(
                        _(
                            "Some categories in different language are children of "
                            "this category, you can't change language until those "
                            "categories are not related anymore or adopted the same "
                            "language."
                        ),
                        code="invalid-language",
                    ),
                )

    class Meta:
        model = Category
        widgets = {
            "description": CKEditorWidget(config_name=CONFIG_NAME),
        }
        fields = "__all__"
