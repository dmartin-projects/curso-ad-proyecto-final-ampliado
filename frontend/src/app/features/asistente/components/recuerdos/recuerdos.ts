import { Component, input, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';

import { Recuerdo } from '../../interfaces/asistente.models';

/**
 * Lo que recuerda el asistente (módulo 99): lo que la persona le pidió recordar, para todas sus conversaciones. Se ve y
 * se borra aquí; viaja en cada pregunta, así que lo que no se ve no debería estar.
 */
@Component({
  selector: 'app-recuerdos',
  imports: [MatButtonModule, MatExpansionModule, MatIconModule],
  templateUrl: './recuerdos.html',
})
export class Recuerdos {
  readonly recuerdos = input.required<Recuerdo[]>();
  readonly olvidar = output<Recuerdo>();
}
