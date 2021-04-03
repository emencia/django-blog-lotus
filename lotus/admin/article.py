# -*- coding: utf-8 -*-
"""
Article admin interface
"""
from django.contrib import admin

from ..models import Article


class ArticleAdmin(admin.ModelAdmin):
    """
    TODO:
        * Fieldset structure to group fields by theme (translation? parameters?
          status? content? relations? dates? etc);
        * How to preselect language ?
        * Enforce FK and M2M selection limit for language ? Or at least FK/M2M
          selections must show the language;
        * Some helper links to add translation for enabled language and
          preselect original object ?
        * Useful list filters;
        * List field displays;
    """
    pass


# Registering interface to model
admin.site.register(Article, ArticleAdmin)
