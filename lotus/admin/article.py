# -*- coding: utf-8 -*-
"""
Article admin interface
"""
from django.contrib import admin

from ..forms import ArticleAdminForm
from ..models import Article


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm


# Registering interface to model
admin.site.register(Article, ArticleAdmin)
