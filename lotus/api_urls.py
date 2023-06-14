"""
API URLs
"""
from django.urls import path, include

from rest_framework import routers

from .viewsets import ArticleViewSet, AuthorViewSet, CategoryViewSet


app_name = "lotus-api"


# API router
router = routers.DefaultRouter()
router.register(
    r"article",
    ArticleViewSet,
    basename="article"
)
router.register(
    r"author",
    AuthorViewSet,
    basename="author"
)
router.register(
    r"category",
    CategoryViewSet,
    basename="category"
)


urlpatterns = [
    path("", include(router.urls)),
]
