import { DatePipe } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { injectMutation, injectQuery, QueryClient } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';

import { SesionActiva } from '../../../../core/api/tipos';
import { Avisos } from '../../../../core/http/avisos';
import { CuentaApi } from '../../services/cuenta-api';

/** Cómo se entró, en palabras (los factores de la sesión). */
const FACTORES: Record<string, string> = {
  contrasena: 'contraseña',
  proveedor: 'proveedor',
  totp: 'código',
  recuperacion: 'código de recuperación',
  passkey: 'passkey',
};

/**
 * Módulo 92: las sesiones abiertas (cada navegador donde se ha entrado, y las páginas donde se da acceso a otras
 * aplicaciones), con el dispositivo, la red aproximada y el último uso. Cerrar una la corta ya: su refresh no renueva y
 * su access se rechaza desde este momento.
 */
@Component({
  selector: 'app-sesiones',
  imports: [DatePipe, MatButtonModule, MatIconModule],
  templateUrl: './sesiones.html',
})
export default class Sesiones {
  private readonly api = inject(CuentaApi);
  private readonly queryClient = inject(QueryClient);
  private readonly avisos = inject(Avisos);

  protected readonly sesiones = injectQuery(() => ({
    queryKey: ['sesiones'],
    queryFn: () => lastValueFrom(this.api.sesiones()),
  }));
  protected readonly hayOtras = computed(() => (this.sesiones.data() ?? []).some((s) => !s.actual));

  protected readonly cerrar = injectMutation(() => ({
    mutationFn: (s: SesionActiva) => lastValueFrom(this.api.cerrarSesion(s.sid)),
    onSuccess: (_: void, s: SesionActiva) => {
      this.avisos.exito(`Sesión de ${s.dispositivo} cerrada`);
      return this.queryClient.invalidateQueries({ queryKey: ['sesiones'] });
    },
  }));

  protected readonly cerrarLasDemas = injectMutation(() => ({
    mutationFn: () => lastValueFrom(this.api.cerrarLasDemas()),
    onSuccess: ({ cerradas }: { cerradas: number }) => {
      this.avisos.exito(cerradas === 1 ? 'Una sesión cerrada' : `${cerradas} sesiones cerradas`);
      return this.queryClient.invalidateQueries({ queryKey: ['sesiones'] });
    },
  }));

  protected factores(s: SesionActiva) {
    return s.factores.map((f) => FACTORES[f] ?? f).join(' + ');
  }
}
