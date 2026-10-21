import { DatePipe } from '@angular/common';
import { Component, computed, input, Resource } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import type { ChartData } from 'chart.js';

import { Grafico } from '../../../../shared/components/grafico/grafico';
import { DiasSemana } from '../../interfaces/dashboard.models';

/**
 * La única tarjeta del dashboard que NO viene de Django, sino del servicio de estadísticas. Va por su
 * cuenta (su propio resource, que le pasa la page) a propósito: si el servicio está caído o va con retraso,
 * esta tarjeta lo dice y el resto del dashboard ni se entera. Recibe un `Resource` (de @angular/core): sabe
 * pintar "cargando", "error" y "datos", no de dónde salen.
 */
@Component({
  selector: 'app-dias-semana',
  imports: [DatePipe, MatCardModule, Grafico],
  templateUrl: './dias-semana.html',
})
export class DiasSemanaCard {
  readonly datos = input.required<Resource<DiasSemana | undefined>>();

  protected readonly grafico = computed<ChartData<'bar'>>(() => {
    const datos = this.datos();
    const dias = datos.hasValue() ? datos.value()!.dias : [];
    return {
      labels: dias.map((d) => d.nombre),
      datasets: [{ label: 'Gasto medio (€)', data: dias.map((d) => Number(d.gasto_medio)) }],
    };
  });
}
