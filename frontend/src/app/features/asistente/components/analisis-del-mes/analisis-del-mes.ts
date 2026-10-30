import { Component, input, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';

/** El botón del análisis del mes y su progreso (módulo 105). Lo lleva AnalisisDelMesStore. */
@Component({
  selector: 'app-analisis-del-mes',
  imports: [MatButtonModule, MatIconModule, MatProgressBarModule],
  templateUrl: './analisis-del-mes.html',
})
export class AnalisisDelMes {
  readonly pasos = input.required<string[]>();
  readonly enCurso = input.required<boolean>();
  readonly error = input('');
  readonly analizar = output();
}
