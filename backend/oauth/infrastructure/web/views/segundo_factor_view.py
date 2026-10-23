# oauth/infrastructure/web/views/segundo_factor_view.py — el segundo paso en el authorization server (módulo 92)
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View
from rest_framework.throttling import ScopedRateThrottle

from core.domain.exceptions.dominio_exception import DominioException
from usuarios.application.completar_segundo_factor_use_case.dtos.completar_segundo_factor_input_dto import (
    CompletarSegundoFactorInputDTO,
)
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.infrastructure import container as cuentas
from usuarios.infrastructure.api.sessions.peticion import contexto_de
from usuarios.infrastructure.api.sessions.sesion_de_django import PENDIENTE_DJANGO, entrar_en_django


class SegundoFactorView(View):
    """El segundo paso en el authorization server: el código de la app (TOTP) o uno de recuperación. (Las passkeys,
    en la SPA: estas páginas no llevan JavaScript; con el MFA activo, siempre hay un TOTP.)"""

    template_name = "oauth/segundo_factor.html"
    throttle_scope = "mfa"

    def _siguiente(self, request) -> str:
        siguiente = request.POST.get("next") or request.GET.get("next") or ""
        seguro = url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}) and siguiente
        return siguiente if seguro and siguiente.startswith("/api/oauth/") else reverse("oauth2_provider:login")

    def _pintar(self, request, status=200, **contexto):
        return render(request, self.template_name, {"next": self._siguiente(request), **contexto}, status=status)

    def get(self, request, *args, **kwargs):
        if not request.session.get(PENDIENTE_DJANGO):
            return HttpResponseRedirect(self._siguiente(request))
        return self._pintar(request)

    def post(self, request, *args, **kwargs):
        if not ScopedRateThrottle().allow_request(request, self):
            return self._pintar(request, 429, error=_("Demasiados intentos. Espera un minuto y vuelve a probar."))
        factor = Factor.RECUPERACION if request.POST.get("factor") == "recuperacion" else Factor.TOTP
        entrada = CompletarSegundoFactorInputDTO(
            request.session.get(PENDIENTE_DJANGO), Canal.AUTORIZACION, factor, request.POST.get("codigo", ""),
            contexto=contexto_de(request),
        )  # fmt: skip
        try:
            sesion, pendiente = cuentas.completar_segundo_factor().ejecutar(entrada)
        except DominioException as error:
            if (
                error.codigo == "login_pendiente_no_valido"
            ):  # caducado o agotado: a la contraseña, con la misma petición
                return HttpResponseRedirect(
                    f"{reverse('oauth2_provider:login')}?{urlencode({'next': self._siguiente(request)})}"
                )
            return self._pintar(request, error.status if error.status == 429 else 400, error=error.mensaje)
        entrar_en_django(request, sesion, pendiente.usuario_id)
        return HttpResponseRedirect(self._siguiente(request))
