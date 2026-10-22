# estadisticas/domain/exceptions/mes_mal_formado_exception.py (módulo 89)


class MesMalFormadoException(ValueError):
    """Un mes que no tiene la forma AAAA-MM. La API responde 422 (infrastructure/api/exceptions)."""
