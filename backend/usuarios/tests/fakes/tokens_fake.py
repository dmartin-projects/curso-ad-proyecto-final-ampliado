# usuarios/tests/fakes/tokens_fake.py — ITokens en memoria (módulo 91)
from usuarios.application.ports.i_tokens import ITokens
from usuarios.domain.vo.par_de_tokens import ParDeTokens


class TokensFake(ITokens):
    def emitir(self, usuario_id):
        return ParDeTokens(access=f"access-{usuario_id}", refresh=f"refresh-{usuario_id}")
