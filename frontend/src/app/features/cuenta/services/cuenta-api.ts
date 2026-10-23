import { HttpClient } from '@angular/common/http';
import { inject, Service } from '@angular/core';

import {
  Acceso,
  AltaTotp,
  AplicacionConectada,
  Seguridad,
  SesionActiva,
} from '../../../core/api/tipos';

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

  // ── Seguridad: verificación en dos pasos y passkeys (módulo 92)
  seguridad() {
    return this.http.get<Seguridad>('/api/v1/auth/seguridad/');
  }

  empezarTotp() {
    return this.http.post<AltaTotp>('/api/v1/auth/seguridad/totp/', null);
  }

  /** El primer código de la app confirma el alta; la respuesta trae los códigos de recuperación. */
  confirmarTotp(datos: { codigo: string }) {
    return this.http.post<{ codigos: string[] }>('/api/v1/auth/seguridad/totp/confirmar/', datos);
  }

  /** Ejercicio 2: códigos de recuperación nuevos (los anteriores dejan de valer). */
  regenerarCodigos() {
    return this.http.post<{ codigos: string[] }>('/api/v1/auth/seguridad/recuperacion/', null);
  }

  desactivarTotp() {
    return this.http.delete('/api/v1/auth/seguridad/totp/');
  }

  retoPasskey() {
    return this.http.post<PublicKeyCredentialCreationOptionsJSON>(
      '/api/v1/auth/seguridad/passkeys/reto/',
      null,
    );
  }

  registrarPasskey(respuesta: RegistrationResponseJSON) {
    return this.http.post('/api/v1/auth/seguridad/passkeys/', { respuesta });
  }

  quitarPasskey(id: number) {
    return this.http.delete(`/api/v1/auth/seguridad/passkeys/${id}/`);
  }

  // ── Sesiones abiertas (módulo 92)
  sesiones() {
    return this.http.get<SesionActiva[]>('/api/v1/auth/sesiones/');
  }

  cerrarSesion(sid: string) {
    return this.http.delete<void>(`/api/v1/auth/sesiones/${sid}/`);
  }

  cerrarLasDemas() {
    return this.http.post<{ cerradas: number }>('/api/v1/auth/sesiones/cerrar-las-demas/', null);
  }
}
