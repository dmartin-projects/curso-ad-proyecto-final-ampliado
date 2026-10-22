import { HttpClient } from '@angular/common/http';
import { inject, Service } from '@angular/core';

import { AplicacionConectada } from '../../../core/api/tipos';

/** "Mi cuenta": lo que la persona ve y cambia de su propia cuenta. */
@Service()
export class CuentaApi {
  private readonly http = inject(HttpClient);

  // ── Aplicaciones conectadas (módulo 90, ejercicio 1)
  aplicaciones() {
    return this.http.get<AplicacionConectada[]>('/api/v1/auth/aplicaciones/');
  }

  retirarAcceso(clientId: string) {
    return this.http.delete<void>(`/api/v1/auth/aplicaciones/${encodeURIComponent(clientId)}/`);
  }
}
