# -*- coding: utf-8 -*-
"""
Article admin interface
"""
from django.contrib import admin

from ..models import Article


class ArticleAdmin(admin.ModelAdmin):
    pass


# Registering interface to model
admin.site.register(Article, ArticleAdmin)
