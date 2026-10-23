import { Component, computed, inject, input, signal } from '@angular/core';
import { email, form, FormField, FormRoot, required } from '@angular/forms/signals';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDividerModule } from '@angular/material/divider';
import { MatInputModule } from '@angular/material/input';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { AuthStore } from '../../../../core/auth/auth-store';
import { mensajeSocial, Social } from '../../../../core/auth/social';
import { ErrorApi } from '../../../../core/http/errores';

@Component({
  selector: 'app-login',
  imports: [
    FormField,
    FormRoot,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    RouterLink,
    MatDividerModule,
  ],
  templateUrl: './login.html',
})
export default class Login {
  private readonly auth = inject(AuthStore);
  private readonly router = inject(Router);
  readonly volver = input<string>(); // ?volver=/hogares/3/tickets (withComponentInputBinding)
  // Módulo 91: con lo que vuelve el backend si el inicio de sesión con un proveedor no se completa
  readonly codigoSocial = input<string>(undefined, { alias: 'error_social' });
  readonly proveedor = input<string>();
  protected readonly social = inject(Social);
  protected readonly errorSocial = computed(() => {
    const codigo = this.codigoSocial();
    return codigo ? mensajeSocial(codigo, this.social.nombre(this.proveedor())) : null;
  });
  protected readonly nombres = computed(() =>
    this.social
      .proveedores()
      .map((p) => p.nombre)
      .join(', '),
  );
  protected readonly error = signal<string | null>(null);
  protected readonly modelo = signal({ email: '', password: '' });

  protected readonly f = form(
    this.modelo,
    (r) => {
      required(r.email, { message: 'Escribe tu email' });
      email(r.email, { message: 'No parece un email' });
      required(r.password);
    },
    {
      submission: {
        action: async () => {
          this.error.set(null);
          try {
            await firstValueFrom(this.auth.login(this.modelo().email, this.modelo().password));
            await this.router.navigateByUrl(this.volver() ?? '/hogares');
          } catch (e) {
            const mensajes: Record<number, string> = {
              401: 'Email o contraseña incorrectos.',
              429: 'Demasiados intentos. Espera un minuto y vuelve a probar.',
            };
            this.error.set((e instanceof ErrorApi && mensajes[e.status]) || 'No se pudo entrar.');
          }
          return null;
        },
      },
    },
  );
}
