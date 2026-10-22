// infra/local/vercel-local.mjs — un "Vercel" de bolsillo para ensayar en tu máquina (módulo 86). Sin dependencias.
//
// No lee vercel.json: lee lo que el `vercel build` DE VERDAD genera a partir de él (.vercel/output/config.json
// y .vercel/output/static), y aplica sus rutas como lo hace Vercel: en orden, con "continue", las fases
// "filesystem" y "error", las variables de entorno de cada entorno en `dest` y en `transforms`, y el proxy
// a orígenes externos con las cabeceras que Vercel añade (x-forwarded-for SOBRESCRITA, x-real-ip…).
// Es un subconjunto (lo que usa Gastos), no Vercel: sin funciones, sin caché de CDN, sin WebSockets.
//
//   cd frontend && vercel build                       # o: npx vercel@65 build (sin cuenta: ver el módulo)
//   node ../infra/local/vercel-local.mjs .vercel/output entornos.json
//
// entornos.json: { "puerto": 8443, "cert": "cert.pem", "clave": "clave.pem",
//   "hosts": { "gastos.tudominio.test": "production", "staging.gastos.tudominio.test": "preview" },
//   "env": { "production": { "API_ORIGEN": "https://api.gastos.tudominio.test", "ORIGEN_SECRETO": "…" },
//            "preview":    { "API_ORIGEN": "https://api.staging.gastos.tudominio.test", "ORIGEN_SECRETO": "…" } } }
import { randomUUID } from 'node:crypto';
import { existsSync, readFileSync, statSync, createReadStream } from 'node:fs';
import http from 'node:http';
import https from 'node:https';
import { dirname, extname, join, normalize, resolve } from 'node:path';

const [salida, archivoEntornos] = process.argv.slice(2);
const entornos = JSON.parse(readFileSync(archivoEntornos, 'utf8'));
const { routes } = JSON.parse(readFileSync(join(salida, 'config.json'), 'utf8'));
const estaticos = join(salida, 'static');
const TIPOS = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.webmanifest': 'application/manifest+json',
  '.ico': 'image/x-icon',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.txt': 'text/plain',
};
const SALTO = [
  'connection',
  'keep-alive',
  'transfer-encoding',
  'upgrade',
  'proxy-connection',
  'te',
  'trailer',
];

const archivo = (ruta) => {
  const p = normalize(join(estaticos, decodeURIComponent(ruta)));
  if (!p.startsWith(estaticos)) return null;
  if (existsSync(p) && statSync(p).isFile()) return p;
  if (existsSync(join(p, 'index.html'))) return join(p, 'index.html');
  return null;
};

// $1, $nombre (grupos de src) y ${VAR}/$VAR (solo las variables de la lista "env" de la ruta o del transform)
function sustituir(plantilla, m, permitidas, env) {
  return plantilla.replace(/\$\{(\w+)\}|\$(\w+)/g, (todo, a, b) => {
    const k = a ?? b;
    if (/^\d+$/.test(k)) return m[Number(k)] ?? '';
    if (m.groups && k in m.groups) return m.groups[k] ?? '';
    if (permitidas?.includes(k) && k in env) return env[k];
    return todo; // como Vercel: si no está, se queda literal
  });
}

function enrutar(req) {
  const host = (req.headers.host ?? '').split(':')[0];
  const entorno = entornos.hosts[host];
  const env = entornos.env[entorno] ?? {};
  const url = new URL(req.url, `https://${host}`);
  let ruta = url.pathname;
  const cabeceras = {}; // de la respuesta, acumuladas por las rutas con "continue"
  const transformaciones = [];
  let fase = null;
  for (const r of routes) {
    if (r.handle) {
      if (r.handle === 'filesystem') {
        const f = archivo(ruta);
        if (f) return { tipo: 'archivo', f, cabeceras };
      }
      fase = r.handle;
      continue;
    }
    if (fase === 'error') continue; // se trata abajo
    const m = new RegExp(r.src).exec(ruta);
    if (!m) continue;
    for (const t of r.transforms ?? []) {
      const v = t.args === undefined ? undefined : sustituir(String(t.args), m, t.env, env);
      transformaciones.push({ ...t, valor: v });
    }
    for (const [k, v] of Object.entries(r.headers ?? {}))
      cabeceras[k.toLowerCase()] = sustituir(v, m, [], {});
    const destino = r.dest ? sustituir(r.dest, m, r.env, env) : null;
    if (r.continue) {
      if (destino) ruta = destino;
      continue;
    }
    if (destino && /^https?:\/\//.test(destino))
      return {
        tipo: 'proxy',
        destino,
        url,
        cabeceras,
        transformaciones,
        entorno,
      };
    if (r.status && !destino) return { tipo: 'estado', estado: r.status, cabeceras };
    if (destino) ruta = destino.split('?')[0];
    if (r.check && !archivo(ruta)) continue;
    const f = archivo(ruta);
    if (f) return { tipo: 'archivo', f, cabeceras, estado: r.status };
  }
  return { tipo: 'estado', estado: 404, cabeceras };
}

function proxy(req, res, d) {
  const destino = new URL(d.destino);
  for (const [k, v] of d.url.searchParams)
    if (!destino.searchParams.has(k)) destino.searchParams.append(k, v);
  const ip = req.socket.remoteAddress.replace(/^::ffff:/, '');
  const h = {};
  for (const [k, v] of Object.entries(req.headers))
    if (!SALTO.includes(k) && k !== 'host') h[k] = v;
  Object.assign(h, {
    host: destino.host, // el del ORIGEN (la API), no el de Vercel
    'x-forwarded-host': req.headers.host,
    'x-forwarded-proto': 'https',
    'x-forwarded-for': ip, // Vercel SOBRESCRIBE lo que mande el cliente (anti-spoofing)
    'x-real-ip': ip,
    'x-vercel-forwarded-for': ip,
    'x-vercel-id': `local::${randomUUID().slice(0, 8)}`,
  });
  for (const t of d.transformaciones) {
    if (t.type !== 'request.headers') continue;
    const k = t.target.key.toLowerCase();
    if (t.op === 'set') h[k] = t.valor;
    else if (t.op === 'delete') delete h[k];
    else if (t.op === 'append') h[k] = h[k] ? `${h[k]}, ${t.valor}` : t.valor;
  }
  const salidaReq = (destino.protocol === 'https:' ? https : http).request(
    destino,
    { method: req.method, headers: h, timeout: 120_000 },
    (r) => {
      const hs = { ...r.headers, ...d.cabeceras };
      for (const k of SALTO) delete hs[k];
      res.writeHead(r.statusCode, hs);
      r.pipe(res);
    },
  );
  salidaReq.on('timeout', () => salidaReq.destroy(new Error('ROUTER_EXTERNAL_TARGET_ERROR')));
  salidaReq.on('error', (e) => {
    if (!res.headersSent) res.writeHead(502, { 'content-type': 'text/plain' });
    res.end(`ROUTER_EXTERNAL_TARGET_ERROR: ${e.message}`);
  });
  req.pipe(salidaReq);
}

const servidor = https.createServer(
  {
    // rutas relativas a entornos.json
    cert: readFileSync(resolve(dirname(archivoEntornos), entornos.cert)),
    key: readFileSync(resolve(dirname(archivoEntornos), entornos.clave)),
  },
  (req, res) => {
    const d = enrutar(req);
    const marca = `${req.method} ${req.headers.host}${req.url}`;
    if (d.tipo === 'proxy') {
      console.log(`${marca} → ${d.destino} [${d.entorno}]`);
      return proxy(req, res, d);
    }
    if (d.tipo === 'archivo') {
      const tipo = TIPOS[extname(d.f)] ?? 'application/octet-stream';
      const cache = d.cabeceras['cache-control'] ?? 'public, max-age=0, must-revalidate'; // el de Vercel
      console.log(`${marca} → ${d.f.slice(estaticos.length)} ${d.estado ?? 200}`);
      res.writeHead(d.estado ?? 200, {
        ...d.cabeceras,
        'content-type': tipo,
        'cache-control': cache,
      });
      return createReadStream(d.f).pipe(res);
    }
    console.log(`${marca} → ${d.estado}`);
    res.writeHead(d.estado, { ...d.cabeceras, 'content-type': 'text/plain' });
    res.end(`${d.estado}\n`);
  },
);
// Vercel no hace de proxy de WebSockets: la conexión se corta
servidor.on('upgrade', (req, socket) => {
  console.log(`UPGRADE ${req.headers.host}${req.url} → rechazado (Vercel no reenvía WebSockets)`);
  socket.end('HTTP/1.1 404 Not Found\r\n\r\n');
});
servidor.listen(entornos.puerto, entornos.ip ?? '127.0.0.1', () =>
  console.log(`vercel-local en https://${entornos.ip ?? '127.0.0.1'}:${entornos.puerto}`),
);
