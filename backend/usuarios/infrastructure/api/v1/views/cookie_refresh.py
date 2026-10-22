# usuarios/infrastructure/api/v1/views/cookie_refresh.py — el refresh token, en una cookie httpOnly (módulos 35 y 88)
from django.conf import settings


def poner_cookie_refresh(response, refresh: str):
    cfg = settings.JWT_REFRESH_COOKIE
    response.set_cookie(
        cfg["key"],
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path=cfg["path"],
        httponly=cfg["httponly"],
        secure=cfg["secure"],
        samesite=cfg["samesite"],
    )
