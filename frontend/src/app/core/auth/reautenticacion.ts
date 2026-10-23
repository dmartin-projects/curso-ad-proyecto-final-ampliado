import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject, Injector, Service } from '@angular/core';
import { catchError, firstValueFrom, from, switchMap, throwError } from 'rxjs';

/**
 * Módulo 92: el step-up. Una acción sensible (cambiar la contraseña, activar el MFA, borrar un hogar…) responde 401 con
 * el reto del RFC 9470 si la sesión no se autenticó hace poco:
 *   WWW-Authenticate: Bearer error="insufficient_user_authentication", max_age="300"
 * El interceptor lo reconoce, pide confirmar (contraseña, código o passkey) y REPITE la petición: el backend apunta la
 * nueva autenticación en la sesión, así que el mismo access token ya vale. Quien la hizo no se entera.
 */
export function esReautenticacion(error: unknown): boolean {
  return (
    error instanceof HttpErrorResponse &&
    error.status === 401 &&
    !!error.headers.get('WWW-Authenticate')?.includes('insufficient_user_authentication')
  );
}

export const reautenticacionInterceptor: HttpInterceptorFn = (req, next) => {
  const reautenticacion = inject(Reautenticacion);
  return next(req).pipe(
    catchError((error: unknown) =>
      esReautenticacion(error)
        ? from(reautenticacion.confirmar()).pipe(
            switchMap((hecho) => (hecho ? next(req) : throwError(() => error))),
          )
        : throwError(() => error),
    ),
  );
};

/**
 * Una sola ventana aunque varias peticiones pidan confirmar a la vez.
 *
 * El diálogo se descarga la primera vez que hace falta (lazy loading con import()): el interceptor está en la
 * configuración de la app, y con imports estáticos el diálogo, MatDialog y los signal forms irían en el bundle
 * inicial de todas las visitas (unos 180 kB, por encima del presupuesto de 800 kB de angular.json) para algo que
 * casi nunca se abre.
 */
@Service()
export class Reautenticacion {
  private readonly injector = inject(Injector);
  private enCurso: Promise<boolean> | null = null;

  confirmar(): Promise<boolean> {
    this.enCurso ??= this.abrir().finally(() => (this.enCurso = null));
    return this.enCurso;
  }

  private async abrir(): Promise<boolean> {
    const [{ MatDialog }, { DialogoReautenticar }] = await Promise.all([
      import('@angular/material/dialog'),
      import('./dialogo-reautenticar/dialogo-reautenticar'),
    ]);
    // MatDialog es providedIn: 'root': el injector lo crea la primera vez que se pide
    const dialogo = this.injector.get(MatDialog).open(DialogoReautenticar, { width: '400px' });
    return (await firstValueFrom(dialogo.afterClosed())) === true;
  }
}
