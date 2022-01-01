"""
Application URLs
"""
from django.urls import path

from .views import (
    ArticleIndexView, ArticleDetailView,
    AuthorIndexView, AuthorDetailView,
    CategoryIndexView, CategoryDetailView,
)


app_name = "lotus"


urlpatterns = [
    path("", ArticleIndexView.as_view(), name="article-index"),
    path(
        'articles/<int:year>/<int:month>/<int:day>/<slug:slug>/',
        ArticleDetailView.as_view(),
        name="article-detail"
    ),

    path("authors/", AuthorIndexView.as_view(), name="author-index"),
    path(
        "authors/<slug:username>/",
        AuthorDetailView.as_view(),
        name="author-detail"
    ),

    path("categories/", CategoryIndexView.as_view(), name="category-index"),
    path(
        "categories/<slug:slug>/",
        CategoryDetailView.as_view(),
        name="category-detail"
    ),
]
