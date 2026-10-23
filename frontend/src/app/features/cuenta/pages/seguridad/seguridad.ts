import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { form, FormField, FormRoot, required } from '@angular/forms/signals';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { injectQuery, QueryClient } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';

import { AltaTotp, PasskeyRegistrada } from '../../../../core/api/tipos';
import { esCancelacion, Passkeys } from '../../../../core/auth/passkeys';
import { Social } from '../../../../core/auth/social';
import { Avisos } from '../../../../core/http/avisos';
import { erroresDelServidor } from '../../../../core/http/errores-formulario';
import { Confirmaciones } from '../../../../shared/components/confirmar/confirmaciones';
import { CuentaApi } from '../../services/cuenta-api';

/**
 * Módulo 92: la verificación en dos pasos (TOTP y códigos de recuperación) y las passkeys. Todo lo que cambia la forma
 * de entrar es una acción sensible: si la sesión no es reciente, el backend responde con el reto del step-up y el
 * interceptor pide confirmar antes de repetir la petición (core/auth/reautenticacion.ts). Aquí no hay que hacer nada.
 */
@Component({
  selector: 'app-seguridad',
  imports: [
    DatePipe,
    FormField,
    FormRoot,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
  ],
  templateUrl: './seguridad.html',
})
export default class Seguridad {
  private readonly api = inject(CuentaApi);
  private readonly queryClient = inject(QueryClient);
  private readonly avisos = inject(Avisos);
  private readonly confirmaciones = inject(Confirmaciones);
  private readonly passkeys = inject(Passkeys);
  protected readonly social = inject(Social);

  protected readonly seguridad = injectQuery(() => ({
    queryKey: ['seguridad'],
    queryFn: () => lastValueFrom(this.api.seguridad()),
  }));
  protected readonly alta = signal<AltaTotp | null>(null);
  protected readonly codigos = signal<string[] | null>(null);
  /** El rp_id es el dominio de la app: en una preview de Vercel, el navegador no dejaría crear una passkey de Gastos. */
  protected puedeAnadir() {
    return this.passkeys.disponible() && this.social.disponible();
  }

  private readonly modelo = signal({ codigo: '' });
  protected readonly f = form(
    this.modelo,
    (r) => required(r.codigo, { message: 'Escribe el código' }),
    {
      submission: {
        action: async (f) => {
          try {
            const { codigos } = await lastValueFrom(this.api.confirmarTotp(this.modelo()));
            this.alta.set(null);
            this.codigos.set(codigos);
            await this.refrescar();
          } catch (e) {
            return erroresDelServidor(e, f);
          }
          return null;
        },
      },
    },
  );

  protected async empezar() {
    this.alta.set(await lastValueFrom(this.api.empezarTotp()));
  }

  /** Ejercicio 2: códigos nuevos (los anteriores dejan de valer). Acción sensible: el step-up, si hace falta. */
  protected async regenerar() {
    const seguro = await this.confirmaciones.preguntar(
      '¿Generar códigos de recuperación nuevos?',
      'Los que tienes ahora dejarán de valer.',
      'Generar',
    );
    if (!seguro) return;
    const { codigos } = await lastValueFrom(this.api.regenerarCodigos());
    this.codigos.set(codigos);
    await this.refrescar();
  }

  protected async desactivar() {
    const seguro = await this.confirmaciones.preguntar(
      '¿Desactivar la verificación en dos pasos?',
      'Con tu contraseña bastará para entrar. Tus códigos de recuperación dejarán de valer.',
      'Desactivar',
    );
    if (!seguro) return;
    await lastValueFrom(this.api.desactivarTotp());
    this.avisos.exito('Verificación en dos pasos desactivada');
    await this.refrescar();
  }

  protected async anadirPasskey() {
    try {
      const opciones = await lastValueFrom(this.api.retoPasskey());
      const respuesta = await this.passkeys.crear(opciones);
      await lastValueFrom(this.api.registrarPasskey(respuesta));
      this.avisos.exito('Passkey añadida');
      await this.refrescar();
    } catch (e) {
      if (!esCancelacion(e)) this.avisos.error('No se ha podido añadir la passkey.');
    }
  }

  protected async borrar(p: PasskeyRegistrada) {
    const seguro = await this.confirmaciones.preguntar(
      `¿Quitar «${p.nombre}»?`,
      'Ya no podrás entrar con ella. (En el dispositivo seguirá guardada: bórrala también allí.)',
      'Quitar',
    );
    if (!seguro) return;
    await lastValueFrom(this.api.quitarPasskey(p.id));
    this.avisos.exito(`«${p.nombre}» quitada`);
    await this.refrescar();
  }

  private refrescar() {
    return this.queryClient.invalidateQueries({ queryKey: ['seguridad'] });
  }
}
