from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from dishes.views import home

urlpatterns = [
        # Admin panel
    path("admin/", admin.site.urls, name="custom_admin"),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API URLs
    path("auth/", include("users.urls")),
    path("categories/", include("categories.urls")),
    path("recipes/", include("dishes.urls")),
    # Translation management (rosetta)
    path("rosetta/", include("rosetta.urls")),
     # Docs
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
     # Downloadable Schema (YML)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path('', home, name='home'),
]

# # Internationalization patterns
# urlpatterns += i18n_patterns(
#     path("admin/", admin.site.urls), prefix_default_language=False
# )

# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
