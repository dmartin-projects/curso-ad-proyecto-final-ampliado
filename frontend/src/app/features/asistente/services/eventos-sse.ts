import { EventoChat } from '../interfaces/asistente.models';

/**
 * Lee Server-Sent Events de un texto que va creciendo (el `partialText` de cada evento de progreso de la petición):
 * devuelve los eventos COMPLETOS que aún no había devuelto. Un evento termina en una línea en blanco; lo que queda
 * a medias se lee en la siguiente llamada. Las líneas que empiezan por ":" son comentarios (los latidos).
 */
export class LectorSSE {
  private leido = 0;

  leer(texto: string): EventoChat[] {
    const fin = texto.lastIndexOf('\n\n');
    if (fin < this.leido) return [];
    const bloques = texto.slice(this.leido, fin).split('\n\n');
    this.leido = fin + 2;
    return bloques.flatMap((bloque) => {
      let evento = '';
      let datos = '';
      for (const linea of bloque.split('\n')) {
        if (linea.startsWith('event: ')) evento = linea.slice(7);
        else if (linea.startsWith('data: ')) datos += linea.slice(6);
      }
      return evento ? [{ ...JSON.parse(datos || '{}'), evento } as EventoChat] : [];
    });
  }
}
