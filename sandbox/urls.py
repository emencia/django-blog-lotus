"""
URL Configuration for sandbox
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from lotus.sitemaps import ArticleSitemap, AuthorSitemap, CategorySitemap, TagSitemap

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

# The sitemap.xml part
sitemap_classes = {
    "lotus-article": ArticleSitemap,
    "lotus-author": AuthorSitemap,
    "lotus-category": CategorySitemap,
    "lotus-tag": TagSitemap,
}

urlpatterns += [
    path("sitemap.xml", sitemap_views.index, {"sitemaps": sitemap_classes}),
    path(
        "sitemap-<section>.xml",
        sitemap_views.sitemap,
        {"sitemaps": sitemap_classes},
        name="django.contrib.sitemaps.views.sitemap"
    ),
]

# Enable API if DRF is installed
try:
    import rest_framework  # noqa: F401
except ModuleNotFoundError:
    API_AVAILABLE = False
else:
    API_AVAILABLE = True
    urlpatterns += [
        path("api/", include("lotus.api_urls")),
    ]

    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
    urlpatterns += [
        # YOUR PATTERNS
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        # Optional UI:
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# Mount Lotus frontend with I18N
urlpatterns += i18n_patterns(
    path("", include("lotus.urls")),
)

# This is only needed when using runserver with settings "DEBUG" enabled
if settings.DEBUG:
    urlpatterns = (
        urlpatterns
        + staticfiles_urlpatterns()
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
