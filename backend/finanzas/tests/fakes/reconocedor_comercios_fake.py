# finanzas/tests/fakes/reconocedor_comercios_fake.py — IReconocedorComercios en memoria (módulo 87)
from finanzas.application.ports.i_reconocedor_comercios import IReconocedorComercios
from finanzas.domain.services.normalizacion import normalizar


class ReconocedorComerciosFake(IReconocedorComercios):
    def __init__(self, **comercios: int):  # mercadona=1
        self._comercios = {normalizar(nombre): pk for nombre, pk in comercios.items()}

    def reconocer(self, texto):
        normalizado = normalizar(texto)
        return next((pk for nombre, pk in self._comercios.items() if nombre in normalizado), None)
