import { DatePipe, DecimalPipe } from '@angular/common';
import { Component, computed, input } from '@angular/core';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { Cuota } from '../../interfaces/asistente.models';

/**
 * Lo que queda de la cuota del asistente (módulo 98). En tokens, porque es lo que se gasta; con una pista de cuántas
 * preguntas son (una normal gasta unos 6.000), que es lo que entiende quien pregunta.
 */
@Component({
  selector: 'app-cuota',
  imports: [DatePipe, DecimalPipe, MatProgressBarModule],
  templateUrl: './cuota.html',
})
export class CuotaDelAsistente {
  readonly cuota = input.required<Cuota>();
  protected readonly usado = computed(() =>
    Math.min(100, (100 * this.cuota().tokens_hoy) / this.cuota().tokens_dia),
  );
  protected readonly preguntas = computed(() =>
    Math.max(
      0,
      Math.floor((this.cuota().tokens_dia - this.cuota().tokens_hoy) / TOKENS_POR_PREGUNTA),
    ),
  );
}

const TOKENS_POR_PREGUNTA = 6000;
