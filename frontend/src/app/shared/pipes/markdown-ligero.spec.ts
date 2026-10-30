import { MarkdownLigero } from './markdown-ligero';

describe('MarkdownLigero', () => {
  const md = new MarkdownLigero();

  it('negritas, listas y saltos de línea', () => {
    expect(md.transform('En **septiembre**:\n- Súper: 461,35 €\n- Ocio\nFin')).toBe(
      'En <strong>septiembre</strong>:<br><ul><li>Súper: 461,35 €</li><li>Ocio</li></ul>Fin',
    );
  });

  it('escapa antes de añadir nada: ni etiquetas ni atributos del texto', () => {
    expect(md.transform('<img src=x onerror="alert(1)"> **hola**')).toBe(
      '&lt;img src=x onerror=&quot;alert(1)&quot;&gt; <strong>hola</strong>',
    );
  });
});
