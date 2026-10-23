import { HttpClient, HttpContext } from '@angular/common/http';
import { computed, inject, Service } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, of } from 'rxjs';

import { ProveedoresSociales } from '../api/tipos';
import { SIN_AUTH, SIN_AVISO_ERROR } from '../http/contexto';

/** Lo que significa cada `error_social` con el que vuelve el backend (módulo 91), en palabras de la persona. */
export const ERRORES_SOCIALES: Record<string, string> = {
  estado_no_valido: 'El inicio de sesión ha caducado o no se empezó aquí. Vuelve a intentarlo.',
  login_social_no_valido: 'No se ha podido completar el inicio de sesión. Vuelve a intentarlo.',
  acceso_cancelado: 'Has cancelado el inicio de sesión.',
  proveedor_no_disponible: 'Ese proveedor no está disponible.',
  email_no_verificado:
    'Tu cuenta de {proveedor} no tiene un email verificado. Verifícalo allí y vuelve a intentarlo.',
  cuenta_existente:
    'Ya tienes una cuenta en Gastos con ese email. Entra con tu contraseña y vincula {proveedor} desde «Métodos de acceso».',
  cuenta_desactivada: 'Esta cuenta está desactivada.',
  identidad_de_otra_cuenta: 'Esa cuenta de {proveedor} ya está vinculada a otro usuario de Gastos.',
  proveedor_ya_vinculado: 'Ya tienes otra cuenta de {proveedor} vinculada: desvincúlala antes.',
};

/** El mensaje de un `error_social`, con el nombre del proveedor ("Google"). */
export function mensajeSocial(codigo: string, proveedor: string): string {
  const plantilla = ERRORES_SOCIALES[codigo] ?? 'No se ha podido completar el inicio de sesión.';
  return plantilla.replace('{proveedor}', proveedor);
}

/** `location`, detrás de un servicio: en los tests no se navega de verdad. */
@Service()
export class Navegador {
  origen() {
    return location.origin;
  }

  ir(url: string) {
    location.assign(url);
  }
}

/**
 * Los proveedores con los que se puede entrar (Google, GitHub, Apple). La ida y la vuelta las hace Django (patrón BFF):
 * la SPA solo navega a /api/v1/auth/social/<id>/entrar/ y, a la vuelta, recupera la sesión con su refresh de siempre.
 *
 * Solo se ofrecen en el dominio de la app (`origen`): una preview de Vercel tiene otra URL, que no está registrada en
 * ningún proveedor como vuelta, y la cookie de la sesión quedaría en el dominio de staging, no en el de la preview.
 */
@Service()
export class Social {
  private readonly http = inject(HttpClient);
  private readonly navegador = inject(Navegador);

  private readonly datos = toSignal(
    this.http
      .get<ProveedoresSociales>('/api/v1/auth/social/', {
        context: new HttpContext().set(SIN_AUTH, true).set(SIN_AVISO_ERROR, true),
      })
      .pipe(catchError(() => of(null))),
    { initialValue: null },
  );

  readonly proveedores = computed(() => this.datos()?.proveedores ?? []);
  readonly origen = computed(() => this.datos()?.origen ?? null);
  /** ¿Se puede entrar con un proveedor desde aquí? (en una preview, no) */
  readonly disponible = computed(() => this.origen() === this.navegador.origen());

  /** "google" → "Google": los nombres los da el backend (un proveedor nuevo no toca la SPA). */
  nombre(id?: string): string {
    return this.proveedores().find((p) => p.id === id)?.nombre ?? 'el proveedor';
  }

  urlEntrar(proveedor: string, volver?: string): string {
    const params = volver ? `?${new URLSearchParams({ volver })}` : '';
    return `/api/v1/auth/social/${encodeURIComponent(proveedor)}/entrar/${params}`;
  }
}
