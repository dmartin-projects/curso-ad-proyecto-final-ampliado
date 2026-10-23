# usuarios/tests/fakes/codigo_qr_fake.py — ICodigoQr en memoria (módulo 92)
from usuarios.application.ports.i_codigo_qr import ICodigoQr


class CodigoQrFake(ICodigoQr):
    def svg(self, texto):
        return f"data:image/svg+xml,{texto}"
