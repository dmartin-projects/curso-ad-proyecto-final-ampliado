import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { form, FormField, FormRoot, required } from '@angular/forms/signals';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { lastValueFrom } from 'rxjs';

import { FactoresReautenticacion } from '../../api/tipos';
import { ErrorApi } from '../../http/errores';
import { esCancelacion, Passkeys } from '../passkeys';
import { Navegador, Social } from '../social';

/** La ventana del step-up: confirmar con la contraseña, un código o una passkey (la abre Reautenticacion). */
@Component({
  selector: 'app-reautenticar',
  imports: [
    FormField,
    FormRoot,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './dialogo-reautenticar.html',
})
export class DialogoReautenticar {
  private readonly http = inject(HttpClient);
  private readonly ref = inject<MatDialogRef<DialogoReautenticar, boolean>>(MatDialogRef);
  private readonly navegador = inject(Navegador);
  protected readonly passkeys = inject(Passkeys);
  protected readonly social = inject(Social);
  protected readonly factores = signal<FactoresReautenticacion | null>(null);
  protected readonly conTotp = signal(false);
  protected readonly error = signal<string | null>(null);
  private readonly modelo = signal({ codigo: '' });

  protected readonly formulario = form(this.modelo, (r) => required(r.codigo), {
    submission: {
      action: async () => {
        const factor = this.conTotp() ? 'totp' : 'contrasena';
        await this.enviar({ factor, codigo: this.modelo().codigo });
        return null;
      },
    },
  });

  constructor() {
    this.http.get<FactoresReautenticacion>('/api/v1/auth/reautenticar/').subscribe((f) => {
      this.factores.set(f);
      this.conTotp.set(f.factores.includes('totp'));
    });
  }

  protected async conPasskey() {
    try {
      const opciones = await lastValueFrom(
        this.http.post<PublicKeyCredentialRequestOptionsJSON>(
          '/api/v1/auth/reautenticar/reto/',
          null,
        ),
      );
      await this.enviar({ factor: 'passkey', respuesta: await this.passkeys.firmar(opciones) });
    } catch (e) {
      if (!esCancelacion(e)) this.error.set('No se ha podido usar la passkey.');
    }
  }

  /** Sin contraseña ni passkeys: una entrada nueva con su proveedor (vuelve a esta misma página). */
  protected conProveedor(proveedor: string) {
    this.navegador.ir(this.social.urlEntrar(proveedor, location.pathname));
  }

  private async enviar(datos: object) {
    this.error.set(null);
    try {
      await lastValueFrom(this.http.post('/api/v1/auth/reautenticar/', datos));
      this.ref.close(true);
    } catch (e) {
      const errores = e instanceof ErrorApi ? Object.values(e.errores).flat() : [];
      this.error.set(
        errores[0] ?? (e instanceof ErrorApi ? e.titulo : 'No se ha podido comprobar.'),
      );
    }
  }
}
