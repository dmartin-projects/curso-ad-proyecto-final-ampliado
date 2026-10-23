import { HttpClient, HttpContext } from '@angular/common/http';
import { computed, inject, Service, signal } from '@angular/core';
import { Router } from '@angular/router';
import { QueryClient } from '@tanstack/angular-query-experimental';
import {
  catchError,
  finalize,
  firstValueFrom,
  map,
  Observable,
  of,
  shareReplay,
  switchMap,
  tap,
} from 'rxjs';

import { Usuario } from '../api/tipos';
import { SIN_AUTH, SIN_AVISO_ERROR } from '../http/contexto';

const SIN_TOKEN = () => new HttpContext().set(SIN_AUTH, true).set(SIN_AVISO_ERROR, true);

/** Módulo 92: lo que contesta un inicio de sesión: la sesión, o que falta el segundo factor (y con qué darlo). */
interface RespuestaInicio {
  access?: string;
  segundo_factor?: string[];
}
export type Inicio = { dentro: true } | { dentro: false; factores: string[] };

/** El segundo paso: un código (TOTP o de recuperación) o la respuesta de una passkey. */
export interface SegundoFactor {
  factor: 'totp' | 'recuperacion' | 'passkey';
  codigo?: string;
  respuesta?: AuthenticationResponseJSON;
}

/**
 * Sesión: el access token vive SOLO en memoria (una signal); el refresh, en una cookie HttpOnly
 * que el navegador envía sola a /api/v1/auth/ (módulos 35 y 51). Nada en localStorage.
 */
@Service()
export class AuthStore {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly queryClient = inject(QueryClient);

  private readonly _access = signal<string | null>(null);
  readonly access = this._access.asReadonly();
  readonly usuario = signal<Usuario | null>(null);
  readonly autenticado = computed(() => this._access() !== null);

  private refrescoEnCurso: Observable<string> | null = null;

  /** Con MFA, la contraseña no da la sesión: el backend deja el login a medias (cookie HttpOnly) y dice con qué seguir. */
  login(email: string, password: string): Observable<Inicio> {
    return this.iniciar(
      this.http.post<RespuestaInicio>(
        '/api/v1/auth/login/',
        { email, password },
        { context: SIN_TOKEN() },
      ),
    );
  }

  /** Módulo 92: con qué se puede completar un login a medias (o un error, si ese primer paso ha caducado). */
  factoresPendientes() {
    return this.http.get<{ factores: string[] }>('/api/v1/auth/mfa/', { context: SIN_TOKEN() });
  }

  /** Módulo 92: el reto que firma la passkey del segundo paso. */
  retoSegundoFactor() {
    return this.http.post<PublicKeyCredentialRequestOptionsJSON>('/api/v1/auth/mfa/reto/', null, {
      context: SIN_TOKEN(),
    });
  }

  /** Módulo 92: el segundo paso del login (la cookie del primero la manda el navegador). */
  completarSegundoFactor(datos: SegundoFactor): Observable<Inicio> {
    return this.iniciar(
      this.http.post<RespuestaInicio>('/api/v1/auth/mfa/', datos, { context: SIN_TOKEN() }),
    );
  }

  /** Módulo 92: el reto que firma una passkey para entrar sin contraseña. */
  retoPasskey() {
    return this.http.post<PublicKeyCredentialRequestOptionsJSON>(
      '/api/v1/auth/passkey/reto/',
      null,
      {
        context: SIN_TOKEN(),
      },
    );
  }

  /** Módulo 92: entrar con una passkey, sin contraseña. */
  entrarConPasskey(respuesta: AuthenticationResponseJSON): Observable<Inicio> {
    return this.iniciar(
      this.http.post<RespuestaInicio>(
        '/api/v1/auth/passkey/',
        { respuesta },
        { context: SIN_TOKEN() },
      ),
    );
  }

  private iniciar(peticion: Observable<RespuestaInicio>): Observable<Inicio> {
    return peticion.pipe(
      switchMap((r): Observable<Inicio> => {
        if (!r.access) return of({ dentro: false, factores: r.segundo_factor ?? [] });
        this._access.set(r.access);
        return this.cargarUsuario().pipe(map(() => ({ dentro: true }) as const));
      }),
    );
  }

  /** Una sola petición de refresh aunque la pidan varias peticiones a la vez. */
  refrescar(): Observable<string> {
    this.refrescoEnCurso ??= this.http
      .post<{ access: string }>('/api/v1/auth/refresh/', null, { context: SIN_TOKEN() })
      .pipe(
        map((r) => r.access),
        tap({ next: (a) => this._access.set(a), error: () => this.limpiar() }),
        finalize(() => (this.refrescoEnCurso = null)),
        shareReplay({ bufferSize: 1, refCount: false }),
      );
    return this.refrescoEnCurso;
  }

  /** Al arrancar: si la cookie de refresh sigue siendo válida, se recupera la sesión sin pedir contraseña. */
  restaurarSesion(): Promise<unknown> {
    return firstValueFrom(
      this.refrescar().pipe(
        switchMap(() => this.cargarUsuario()),
        catchError(() => of(null)),
      ),
    );
  }

  logout() {
    this.http
      .post('/api/v1/auth/logout/', null, { context: SIN_TOKEN() })
      .subscribe({ error: () => undefined }); // si falla (sin red), la sesión local se cierra igual
    this.limpiar();
    this.router.navigateByUrl('/login');
  }

  private cargarUsuario() {
    return this.http.get<Usuario>('/api/v1/auth/me/').pipe(tap((u) => this.usuario.set(u)));
  }

  private limpiar() {
    this._access.set(null);
    this.usuario.set(null);
    this.queryClient.clear(); // los datos cacheados eran de otro usuario
  }
}
