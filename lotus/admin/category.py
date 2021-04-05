# -*- coding: utf-8 -*-
"""
Category admin interface
"""
from django.contrib import admin

from ..forms import CategoryAdminForm
from ..models import Category


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm


# Registering interface to model
admin.site.register(Category, CategoryAdmin)
