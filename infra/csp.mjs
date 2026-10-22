// infra/csp.mjs — la CSP con los hashes de autoCsp, en la salida de `vercel build` (módulos 83 y 86)
// Con "autoCsp", Angular calcula el hash de cada <script> en línea de index.html (el cargador de main.js y el
// que activa la hoja de estilos tras el CSS crítico) y los pone en un <meta>. Una CSP en <meta> no basta:
// la cabecera también se aplica, y la política efectiva es la intersección de las dos. vercel.json no puede
// saber los hashes (cambian con cada versión de index.html): tras `vercel build`, este script cambia el
// script-src de la CSP de .vercel/output/config.json por el de index.html. Lo demás, como en vercel.json.
// Uso (lo hace infra/vercel-desplegar.sh): node infra/csp.mjs .vercel/output
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const salida = process.argv[2];
const html = readFileSync(join(salida, "static", "index.html"), "utf8");
const meta = html.match(/http-equiv="Content-Security-Policy" content="([^"]+)"/);
const scriptSrc = meta?.[1].match(/script-src ([^;]+)/)?.[1];
if (!scriptSrc?.includes("'sha256-")) {
  console.error("index.html sin CSP de autoCsp: ¿falta security.autoCsp en angular.json?");
  process.exit(1);
}
const archivo = join(salida, "config.json");
const config = JSON.parse(readFileSync(archivo, "utf8"));
const conCsp = config.routes.filter((ruta) => ruta.headers?.["Content-Security-Policy"]);
if (conCsp.length !== 1) {
  console.error(`Se esperaba UNA ruta con Content-Security-Policy en ${archivo} y hay ${conCsp.length}`);
  process.exit(1);
}
const [ruta] = conCsp;
// 'strict-dynamic' + hashes: lo que cargue el cargador hereda la confianza
ruta.headers["Content-Security-Policy"] = ruta.headers["Content-Security-Policy"].replace(
  /script-src [^;]+/,
  `script-src ${scriptSrc}`,
);
writeFileSync(archivo, JSON.stringify(config, null, 2));
console.log(ruta.headers["Content-Security-Policy"]);
