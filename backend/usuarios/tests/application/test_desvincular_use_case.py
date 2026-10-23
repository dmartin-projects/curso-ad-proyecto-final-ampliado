"""Quitar un proveedor: las passkeys también cuentan como forma de entrar (módulo 92)."""

from usuarios.tests.application.escenarios_mfa import registrar_passkey
from usuarios.tests.fakes.mundo import Mundo


def test_con_una_passkey_se_puede_quitar_el_ultimo_proveedor():
    from usuarios.application.desvincular_use_case.dtos.desvincular_input_dto import DesvincularInputDTO
    from usuarios.domain.enums.proveedor import Proveedor
    from usuarios.domain.vo.perfil_externo import PerfilExterno

    mundo = Mundo()
    ana = mundo.cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")  # sin contraseña
    mundo.identidades.vincular(ana, PerfilExterno(Proveedor.GOOGLE, "sub-ana", "ana@gmail.com", True))
    registrar_passkey(mundo, ana)
    mundo.desvincular.ejecutar(DesvincularInputDTO(ana, Proveedor.GOOGLE))  # le queda la passkey
    assert mundo.identidades.de_usuario(ana) == {}
