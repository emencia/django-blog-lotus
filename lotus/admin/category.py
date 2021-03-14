# -*- coding: utf-8 -*-
"""
Category admin interface
"""
from django.contrib import admin

from ..models import Category


class CategoryAdmin(admin.ModelAdmin):
    pass


# Registering interface to model
admin.site.register(Category, CategoryAdmin)
