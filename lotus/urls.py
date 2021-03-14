"""
Application URLs
"""
from django.urls import path

from lotus.views import (
    ArticleIndexView, ArticleDetailView,
    CategoryIndexView, CategoryDetailView,
)


app_name = "lotus"


urlpatterns = [
    path("", ArticleIndexView.as_view(), name="article-index"),
    path(
        "<int:article_pk>/",
        ArticleDetailView.as_view(),
        name="article-detail"
    ),

    path("categories/", CategoryIndexView.as_view(), name="category-index"),
    path(
        "categories/<int:category_pk>/",
        CategoryDetailView.as_view(),
        name="category-detail"
    ),
]
