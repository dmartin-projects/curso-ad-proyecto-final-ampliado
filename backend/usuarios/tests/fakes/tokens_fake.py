# usuarios/tests/fakes/tokens_fake.py — ITokens en memoria (módulos 91 y 92)
from usuarios.application.ports.i_tokens import ITokens
from usuarios.domain.vo.par_de_tokens import ParDeTokens


class TokensFake(ITokens):
    def emitir(self, usuario_id, sid):
        return ParDeTokens(access=f"access-{usuario_id}-{sid}", refresh=f"refresh-{usuario_id}", jti=f"jti-{sid}")
