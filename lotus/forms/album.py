from django import forms

from ..models import Album, AlbumItem


class AlbumAdminForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = []
        fields = [
            "title",
        ]


class AlbumItemAdminForm(forms.ModelForm):
    class Meta:
        model = AlbumItem
        exclude = []
        fields = [
            "album",
            "title",
            "order",
            "media",
        ]
        widgets = {
            "order": forms.widgets.NumberInput(
                attrs={"style": "width: 80px !important;"}
            ),
        }
