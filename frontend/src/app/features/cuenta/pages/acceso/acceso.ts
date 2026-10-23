import { DatePipe } from '@angular/common';
import { Component, computed, inject, input, OnInit, signal } from '@angular/core';
import { form, FormField, FormRoot, required } from '@angular/forms/signals';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { Router } from '@angular/router';
import { injectMutation, injectQuery, QueryClient } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';

import { IdentidadVinculada } from '../../../../core/api/tipos';
import { mensajeSocial, Navegador, Social } from '../../../../core/auth/social';
import { Avisos } from '../../../../core/http/avisos';
import { erroresDelServidor } from '../../../../core/http/errores-formulario';
import { Confirmaciones } from '../../../../shared/components/confirmar/confirmaciones';
import { CuentaApi } from '../../services/cuenta-api';

/** Con lo que vuelve el backend tras vincular: ?vinculada=google o ?error_social=…&proveedor=google */
interface Vuelta {
  vinculada?: string;
  codigo?: string;
  proveedor?: string;
}

/**
 * Módulo 91: las formas de entrar de la cuenta. La contraseña (o establecer una, si la cuenta nació con Google) y los
 * proveedores: vincular uno es entrar en él (el backend lo une a ESTA cuenta) y desvincularlo, quitarlo. Nunca el
 * último: sin contraseña ni proveedores no habría forma de volver a entrar (el backend lo impide; aquí, ni se ofrece).
 */
@Component({
  selector: 'app-acceso',
  imports: [
    DatePipe,
    FormField,
    FormRoot,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
  ],
  templateUrl: './acceso.html',
})
export default class Acceso implements OnInit {
  private readonly api = inject(CuentaApi);
  private readonly queryClient = inject(QueryClient);
  private readonly avisos = inject(Avisos);
  private readonly confirmaciones = inject(Confirmaciones);
  private readonly navegador = inject(Navegador);
  private readonly router = inject(Router);
  protected readonly social = inject(Social);

  readonly vinculada = input<string>();
  readonly codigoSocial = input<string>(undefined, { alias: 'error_social' });
  readonly proveedor = input<string>();

  protected readonly acceso = injectQuery(() => ({
    queryKey: ['acceso'],
    queryFn: () => lastValueFrom(this.api.acceso()),
  }));

  protected readonly sinVincular = computed(() => {
    const vinculados = new Set(this.acceso.data()?.identidades.map((i) => i.proveedor));
    return this.social.proveedores().filter((p) => !vinculados.has(p.id));
  });

  protected readonly esElUltimo = computed(() => {
    const a = this.acceso.data();
    return !!a && !a.contrasena && a.identidades.length === 1;
  });

  protected readonly desvinculando = injectMutation(() => ({
    mutationFn: (i: IdentidadVinculada) => lastValueFrom(this.api.desvincular(i.proveedor)),
    onSuccess: (_: void, i: IdentidadVinculada) => {
      this.avisos.exito(`${i.nombre} ya no está vinculada a tu cuenta`);
      return this.queryClient.invalidateQueries({ queryKey: ['acceso'] });
    },
  }));

  protected readonly modelo = signal({ nueva: '' });
  protected readonly f = form(
    this.modelo,
    (r) => required(r.nueva, { message: 'Escribe una contraseña' }),
    {
      submission: {
        action: async (f) => {
          try {
            await lastValueFrom(this.api.establecerPassword(this.modelo()));
          } catch (e) {
            return erroresDelServidor(e, f);
          }
          this.avisos.exito('Contraseña establecida');
          await this.queryClient.invalidateQueries({ queryKey: ['acceso'] });
          return null;
        },
      },
    },
  );

  /** Lo que trajo la vuelta (se guarda al llegar: la URL se limpia para que F5 no lo repita). */
  private readonly vuelta = signal<Vuelta | null>(null);
  protected readonly resultado = computed(() => {
    const v = this.vuelta();
    if (!v) return null;
    return v.vinculada
      ? { bien: true, texto: `Cuenta de ${this.social.nombre(v.vinculada)} vinculada.` }
      : { bien: false, texto: mensajeSocial(v.codigo!, this.social.nombre(v.proveedor)) };
  });

  ngOnInit() {
    const [vinculada, codigo] = [this.vinculada(), this.codigoSocial()];
    if (vinculada || codigo) {
      this.vuelta.set({ vinculada, codigo, proveedor: this.proveedor() });
      this.router.navigate([], { queryParams: {}, replaceUrl: true });
    }
  }

  protected nombres(identidades: IdentidadVinculada[]) {
    return identidades.map((i) => i.nombre).join(' y ');
  }

  /** Vincular es entrar en el proveedor: el backend prepara la ida (con mi sesión) y el navegador va allí. */
  protected async vincular(proveedor: string) {
    const { url } = await lastValueFrom(this.api.vincular(proveedor));
    this.navegador.ir(url);
  }

  protected async desvincular(i: IdentidadVinculada) {
    const seguro = await this.confirmaciones.preguntar(
      `¿Desvincular ${i.nombre}?`,
      `Ya no podrás entrar en Gastos con tu cuenta de ${i.nombre} (${i.email}).`,
      'Desvincular',
    );
    if (seguro) this.desvinculando.mutate(i);
  }
}
