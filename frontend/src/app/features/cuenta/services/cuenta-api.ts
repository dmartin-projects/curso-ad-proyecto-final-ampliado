import { HttpClient } from '@angular/common/http';
import { inject, Service } from '@angular/core';

import { Acceso, AplicacionConectada } from '../../../core/api/tipos';

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

  // ── Métodos de acceso: la contraseña y los proveedores vinculados (módulo 91)
  acceso() {
    return this.http.get<Acceso>('/api/v1/auth/acceso/');
  }

  desvincular(proveedor: string) {
    return this.http.delete<void>(`/api/v1/auth/acceso/${encodeURIComponent(proveedor)}/`);
  }

  establecerPassword(datos: { nueva: string }) {
    return this.http.post('/api/v1/auth/establecer-password/', datos);
  }

  /** Vincular es entrar en el proveedor: el backend prepara la ida (con mi sesión) y dice a dónde ir. */
  vincular(proveedor: string) {
    return this.http.post<{ url: string }>(
      `/api/v1/auth/social/${encodeURIComponent(proveedor)}/vincular/`,
      null,
    );
  }
}
