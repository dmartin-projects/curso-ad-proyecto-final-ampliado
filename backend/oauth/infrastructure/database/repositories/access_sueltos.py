# oauth/infrastructure/database/repositories/access_sueltos.py — los access tokens vivos sin refresh (ejercicio 1 del módulo 90)
from django.utils import timezone
from oauth2_provider.models import get_access_token_model

AccessToken = get_access_token_model()


def access_sueltos(**filtro):
    """Access tokens vigentes sin refresh token (un refresh revocado se lleva el suyo): también son acceso dado."""
    return AccessToken.objects.filter(expires__gt=timezone.now(), refresh_token__isnull=True, **filtro)
