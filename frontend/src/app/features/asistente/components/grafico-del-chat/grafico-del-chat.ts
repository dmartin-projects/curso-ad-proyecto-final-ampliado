import { Component, computed, inject, input, LOCALE_ID, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { Grafico } from '../../../../shared/components/grafico/grafico';
import { datosDeGrafico } from '../../../../shared/utils/datos-de-grafico';
import { GraficoDelChat } from '../../interfaces/asistente.models';

/** Un gráfico de una respuesta, con su botón para fijarlo en el dashboard del hogar. */
@Component({
  selector: 'app-grafico-del-chat',
  imports: [MatButtonModule, MatIconModule, Grafico],
  templateUrl: './grafico-del-chat.html',
})
export class GraficoDelChatCard {
  readonly grafico = input.required<GraficoDelChat>();
  readonly fijable = input(true); // un lector no puede cambiar el dashboard: sin botón
  readonly fijar = output<GraficoDelChat>();
  private readonly locale = inject(LOCALE_ID);
  protected readonly chart = computed(() => datosDeGrafico(this.grafico(), this.locale));
}
