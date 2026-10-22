# finanzas/infrastructure/api/v1/views/roles.py — los roles que la view exige antes de validar (módulo 87)


def roles_de(crear, modificar, eliminar) -> dict:
    """Los roles que la view exige ANTES de validar (403 rápido, como siempre) salen de los use cases: una sola
    fuente de verdad. El use case lo vuelve a exigir, porque no todos sus adaptadores pasan por aquí."""
    return {
        "create": crear.rol_minimo,
        "update": modificar.rol_minimo,
        "partial_update": modificar.rol_minimo,
        "destroy": eliminar.rol_minimo,
    }
