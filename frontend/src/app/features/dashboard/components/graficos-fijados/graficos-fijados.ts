import { Component, inject, input, LOCALE_ID, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { Grafico } from '../../../../shared/components/grafico/grafico';
import { GraficoDeDatos } from '../../../../shared/interfaces/grafico-de-datos';
import { datosDeGrafico } from '../../../../shared/utils/datos-de-grafico';
import { GraficoFijado } from '../../interfaces/dashboard.models';

/** Los gráficos que alguien del hogar fijó desde el chat (módulo 97). */
@Component({
  selector: 'app-graficos-fijados',
  imports: [MatButtonModule, MatCardModule, MatIconModule, Grafico],
  templateUrl: './graficos-fijados.html',
})
export class GraficosFijados {
  readonly graficos = input.required<GraficoFijado[]>();
  readonly puedeQuitar = input(false);
  readonly quitar = output<GraficoFijado>();
  private readonly locale = inject(LOCALE_ID);

  protected chart(g: GraficoDeDatos) {
    return datosDeGrafico(g, this.locale);
  }
}
