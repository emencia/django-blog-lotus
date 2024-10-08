"""
Application URLs
"""
from django.urls import path

from .views import (
    ArticleIndexView, ArticleDetailView,
    AuthorIndexView, AuthorDetailView,
    CategoryIndexView, CategoryDetailView,
    PreviewTogglerView, PreviewArticleDetailView,
    TagIndexView, TagDetailView, TagAutocompleteView,
)


app_name = "lotus"


urlpatterns = [
    path("", ArticleIndexView.as_view(), name="article-index"),

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

    path(
        "preview/disable/",
        PreviewTogglerView.as_view(mode="disable"),
        name="preview-disable"
    ),
    path(
        "preview/enable/",
        PreviewTogglerView.as_view(mode="enable"),
        name="preview-enable"
    ),
    path(
        "preview/articles/<int:year>/<int:month>/<int:day>/<slug:slug>/",
        PreviewArticleDetailView.as_view(),
        name="preview-article-detail"
    ),

    path("tags/", TagIndexView.as_view(), name="tag-index"),
    path(
        "tags/autocomplete/",
        TagAutocompleteView.as_view(),
        name="tag-autocomplete",
    ),
    path(
        "tags/<str:tag>/",
        TagDetailView.as_view(),
        name="tag-detail"
    ),

    path(
        "<int:year>/<int:month>/<int:day>/<slug:slug>/",
        ArticleDetailView.as_view(),
        name="article-detail"
    ),
]
