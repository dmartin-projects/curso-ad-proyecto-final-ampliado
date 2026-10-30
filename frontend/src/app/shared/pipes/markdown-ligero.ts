import { Pipe, PipeTransform } from '@angular/core';

const ESCAPAR: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};

/**
 * El poco Markdown que escribe el asistente (negritas, listas y saltos de línea), a HTML. PRIMERO se escapa todo el
 * texto: lo que venga del modelo no puede meter etiquetas ni atributos (un ticket con "<img onerror=…>" que el modelo
 * repite, módulos 60 y 102). Después, solo se añaden las etiquetas de esta lista. Sin enlaces a propósito: una URL en
 * una respuesta es un canal para sacar datos (exfiltración, módulo 102).
 */
@Pipe({ name: 'markdownLigero' })
export class MarkdownLigero implements PipeTransform {
  transform(texto: string | null | undefined): string {
    const escapado = (texto ?? '').replace(/[&<>"']/g, (c) => ESCAPAR[c]);
    const negritas = escapado.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    const bloques: string[] = [];
    let lista: string[] = [];
    for (const linea of negritas.split('\n')) {
      const elemento = /^\s*[-*•]\s+(.*)$/.exec(linea);
      if (elemento) {
        lista.push(`<li>${elemento[1].trim()}</li>`);
        continue;
      }
      if (lista.length) {
        bloques.push(`<ul>${lista.join('')}</ul>`);
        lista = [];
      }
      bloques.push(linea.trim() ? `${linea}<br>` : '<br>');
    }
    if (lista.length) bloques.push(`<ul>${lista.join('')}</ul>`);
    return bloques.join('').replace(/(<br>)+$/, '');
  }
}
