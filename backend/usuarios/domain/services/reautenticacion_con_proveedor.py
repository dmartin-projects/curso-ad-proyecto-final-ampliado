# usuarios/domain/services/reautenticacion_con_proveedor.py — el step-up con el proveedor (módulo 92, ejercicio 3)
from usuarios.domain.exceptions.reautenticacion_no_reciente_exception import ReautenticacionNoRecienteException
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial

MARGEN_DE_RELOJ = 30  # segundos: el reloj del proveedor y el de Gastos no van a la par


def exigir_reautenticacion(perfil: PerfilExterno, transaccion: TransaccionSocial) -> None:
    """Que el proveedor haya pedido de verdad la contraseña (o su segundo factor) en ESTA ida, y no que haya
    reutilizado la sesión que la persona tenía abierta allí. Lo dice el `auth_time` del ID token: tiene que ser
    posterior al momento en que empezó el step-up. Sin auth_time (el proveedor no lo da), no hay prueba."""
    if perfil.autenticado_en is None or transaccion.desde is None:
        raise ReautenticacionNoRecienteException(proveedor=perfil.proveedor.nombre)
    if perfil.autenticado_en < transaccion.desde - MARGEN_DE_RELOJ:
        raise ReautenticacionNoRecienteException(proveedor=perfil.proveedor.nombre)
