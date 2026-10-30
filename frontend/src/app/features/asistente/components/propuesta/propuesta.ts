import { Component, input, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { PropuestaDelChat } from '../../interfaces/asistente.models';

/** Un cambio que propone el asistente: no está hecho hasta que la persona lo confirma (human-in-the-loop). */
@Component({
  selector: 'app-propuesta',
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './propuesta.html',
})
export class PropuestaCard {
  readonly propuesta = input.required<PropuestaDelChat>();
  readonly confirmar = output<PropuestaDelChat>();
  readonly descartar = output<PropuestaDelChat>();
}
