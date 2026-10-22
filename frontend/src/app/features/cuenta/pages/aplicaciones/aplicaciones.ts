import { DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { injectMutation, injectQuery, QueryClient } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';

import { AplicacionConectada } from '../../../../core/api/tipos';
import { Avisos } from '../../../../core/http/avisos';
import { Confirmaciones } from '../../../../shared/components/confirmar/confirmaciones';
import { CuentaApi } from '../../services/cuenta-api';

/** Lo que significa cada scope, en palabras de la persona (las mismas que la pantalla de consentimiento). */
const SCOPES: Record<string, string> = {
  openid: 'Saber quién eres',
  profile: 'Ver tu nombre, tu idioma y tu zona horaria',
  email: 'Ver tu email',
  'gastos:leer': 'Ver los movimientos, las cuentas y el resumen de tus hogares',
  'gastos:escribir': 'Apuntar movimientos en tus hogares',
};

/**
 * Módulo 90 (ejercicio 1): las aplicaciones a las que has dado acceso a tu cuenta (el CLI, la app móvil…) y el
 * botón para retirárselo. Retirarlo revoca sus tokens en el servidor al momento: deja de funcionar ya.
 */
@Component({
  selector: 'app-aplicaciones',
  imports: [DatePipe, MatButtonModule, MatIconModule],
  templateUrl: './aplicaciones.html',
})
export default class Aplicaciones {
  private readonly api = inject(CuentaApi);
  private readonly queryClient = inject(QueryClient);
  private readonly confirmaciones = inject(Confirmaciones);
  private readonly avisos = inject(Avisos);

  protected readonly aplicaciones = injectQuery(() => ({
    queryKey: ['aplicaciones'],
    queryFn: () => lastValueFrom(this.api.aplicaciones()),
  }));

  protected readonly retirada = injectMutation(() => ({
    mutationFn: (a: AplicacionConectada) => lastValueFrom(this.api.retirarAcceso(a.client_id)),
    onSuccess: (_: void, a: AplicacionConectada) => {
      this.avisos.exito(`«${a.nombre}» ya no tiene acceso a tu cuenta`);
      return this.queryClient.invalidateQueries({ queryKey: ['aplicaciones'] });
    },
  }));

  protected describir(scope: string) {
    return SCOPES[scope] ?? scope;
  }

  protected async retirar(a: AplicacionConectada) {
    const seguro = await this.confirmaciones.preguntar(
      `¿Retirar el acceso a «${a.nombre}»?`,
      'Dejará de funcionar ahora mismo en todos los equipos donde la uses. Para volver a usarla, tendrás que darle acceso otra vez.',
      'Retirar acceso',
    );
    if (seguro) this.retirada.mutate(a);
  }
}
