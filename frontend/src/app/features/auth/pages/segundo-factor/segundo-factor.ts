import { Component, computed, inject, input, signal } from '@angular/core';
import { form, FormField, FormRoot, required } from '@angular/forms/signals';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom, lastValueFrom } from 'rxjs';

import { AuthStore, SegundoFactor as DatosSegundoFactor } from '../../../../core/auth/auth-store';
import { esCancelacion, Passkeys } from '../../../../core/auth/passkeys';
import { ErrorApi } from '../../../../core/http/errores';

/**
 * Módulo 92: el segundo paso del login. Se llega desde el login con contraseña o desde la vuelta de un proveedor; en
 * los dos casos, el primer paso está en una cookie HttpOnly que esta página no ve: solo pregunta con qué se puede
 * completar (GET /auth/mfa/) y lo completa (POST /auth/mfa/).
 */
@Component({
  selector: 'app-segundo-factor',
  imports: [
    FormField,
    FormRoot,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    RouterLink,
  ],
  templateUrl: './segundo-factor.html',
})
export default class SegundoFactor {
  private readonly auth = inject(AuthStore);
  private readonly router = inject(Router);
  protected readonly passkeys = inject(Passkeys);
  readonly volver = input<string>();

  protected readonly factores = signal<string[]>([]);
  protected readonly caducado = signal(false);
  protected readonly conRecuperacion = signal(false);
  protected readonly error = signal<string | null>(null);
  private readonly modelo = signal({ codigo: '' });
  protected readonly factor = computed(() => (this.conRecuperacion() ? 'recuperacion' : 'totp'));

  protected readonly f = form(
    this.modelo,
    (r) => required(r.codigo, { message: 'Escribe el código' }),
    {
      submission: {
        action: async () => {
          await this.completar({ factor: this.factor(), codigo: this.modelo().codigo });
          return null;
        },
      },
    },
  );

  constructor() {
    this.auth.factoresPendientes().subscribe({
      next: (r) => this.factores.set(r.factores),
      error: () => this.caducado.set(true),
    });
  }

  protected async conPasskey() {
    try {
      const reto = await lastValueFrom(this.auth.retoSegundoFactor());
      await this.completar({ factor: 'passkey', respuesta: await this.passkeys.firmar(reto) });
    } catch (e) {
      if (!esCancelacion(e)) this.error.set('No se ha podido usar la passkey.');
    }
  }

  private async completar(datos: DatosSegundoFactor) {
    this.error.set(null);
    try {
      await firstValueFrom(this.auth.completarSegundoFactor(datos));
      await this.router.navigateByUrl(this.volver() ?? '/hogares');
    } catch (e) {
      if (e instanceof ErrorApi && e.tipo === 'login_pendiente_no_valido') this.caducado.set(true);
      const errores = e instanceof ErrorApi ? Object.values(e.errores).flat() : [];
      this.error.set(
        errores[0] ?? (e instanceof ErrorApi ? e.titulo : 'No se ha podido comprobar.'),
      );
    }
  }
}
