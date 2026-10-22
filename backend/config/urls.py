from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.infrastructure.api.views import health

urlpatterns = [
    path("health/live/", health.health_live),
    path("health/ready/", health.health_ready),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/<str:version>/", include("config.api_v1")),  # DRF lee la versión de la URL (ALLOWED_VERSIONS: v1)
]
