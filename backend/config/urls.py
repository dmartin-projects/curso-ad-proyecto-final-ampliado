from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.infrastructure.api.views import health
from oauth.infrastructure.web.views.descubrimiento_view import DescubrimientoView

urlpatterns = [
    path("health/live/", health.health_live),
    path("health/ready/", health.health_ready),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/oauth/", include("oauth.infrastructure.web.urls")),  # módulo 90: antes que api/<version>/
    # Módulo 104: el metadata del authorization server, también donde lo busca primero un cliente MCP. Con un emisor
    # con ruta (…/api/oauth), RFC 8414 §3.1 pone el .well-known DELANTE de la ruta; OIDC, detrás (el de arriba)
    path(".well-known/oauth-authorization-server/api/oauth", DescubrimientoView.as_view()),
    path(".well-known/openid-configuration/api/oauth", DescubrimientoView.as_view()),
    path("api/<str:version>/", include("config.api_v1")),  # DRF lee la versión de la URL (ALLOWED_VERSIONS: v1)
]
