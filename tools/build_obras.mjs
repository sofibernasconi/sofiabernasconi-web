// Genera una página propia por obra (public/obra-<id>.html) a partir de la plantilla public/obra.html.
// Cada página trae su título, descripción, URL oficial (canonical), imagen para redes, ficha
// para Google (JSON-LD) y el contenido ya escrito en el HTML (Google lo lee sin ejecutar código).
// Uso: después de editar obra.html →  node tools/build_obras.mjs
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
import fs from 'fs'; import path from 'path'; import url from 'url';
const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), '..', 'public');
const SITE = 'https://sofiabernasconi.com';
const tpl = fs.readFileSync(path.join(ROOT, 'obra.html'), 'utf8');
const esc = s => String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
const corta = (s,n=158) => { s=s.replace(/\s+/g,' ').trim(); return s.length<=n ? s : s.slice(0,s.lastIndexOf(' ',n-1)).replace(/[,;:·—-]$/,'')+'…'; };

const b = await chromium.launch(); const p = await b.newPage();
const p5local = process.env.P5_LOCAL;
if (p5local) await p.route('**/p5.min.js', r => r.fulfill({ path: p5local, contentType: 'application/javascript' }));
await p.route('**fonts.googleapis.com/**', r => r.abort());
const tmp = path.join(ROOT, '__tmp_obra.html');
let data = null;
for (const pass of [0, 1]) {
  const ids = pass === 0 ? ['convey'] : data.ORDER;
  for (const id of ids) {
    fs.writeFileSync(tmp, tpl.replace('<html lang="es">', `<html lang="es" data-obra="${id}">`));
    await p.goto('file://' + tmp + '?lang=es'); await p.waitForTimeout(300);
    if (!data) { data = await p.evaluate(() => ({ OBRAS, TITLE_EN, ORDER })); continue; }
    const main = await p.evaluate(() => document.getElementById('main').innerHTML);
    const o = data.OBRAS[id], en = data.TITLE_EN[id];
    const titulo = `${o.title} (${o.year}) — Sofía Bernasconi`;
    const tec = o.tecnica ? (o.tecnica.es || o.tecnica) : '';
    const desc = corta((tec ? tec + '. ' : '') + o.es[0]);
    const urlc = `${SITE}/obra-${id}`;
    const img = o.fotos && o.fotos.length ? `${SITE}/assets/${o.fotos[0]}` : `${SITE}/assets/og.jpg`;
    const ld = { '@context':'https://schema.org', '@type':'VisualArtwork', name:o.title, ...(en?{alternateName:en}:{}),
      dateCreated:String(o.year), ...(tec?{artMedium:tec}:{}), description:corta(o.es[0],300), image:img, url:urlc,
      inLanguage:['es','en'], creator:{ '@type':'Person', name:'Sofía Bernasconi Le Roy', url:SITE+'/' } };
    let h = tpl.replace('<html lang="es">', `<html lang="es" data-obra="${id}">`)
      .replace('<meta name="robots" content="noindex,follow">\n', '')
      .replace(/<title>[^<]*<\/title>/, `<title>${esc(titulo)}</title>`)
      .replace(/<meta name="description" content="[^"]*">/, `<meta name="description" content="${esc(desc)}">`)
      .replace(/<link rel="canonical" href="[^"]*">/, `<link rel="canonical" href="${urlc}">\n<link rel="alternate" hreflang="es" href="${urlc}">\n<link rel="alternate" hreflang="en" href="${urlc}?lang=en">\n<link rel="alternate" hreflang="x-default" href="${urlc}">`)
      .replace(/<meta property="og:title" content="[^"]*">/, `<meta property="og:title" content="${esc(titulo)}">`)
      .replace(/<meta property="og:description" content="[^"]*">/, `<meta property="og:description" content="${esc(desc)}">`)
      .replace(/<meta property="og:url" content="[^"]*">/, `<meta property="og:url" content="${urlc}">`)
      .replace(/<meta property="og:image" content="[^"]*">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">/, `<meta property="og:image" content="${img}">`)
      .replace(/<meta name="twitter:title" content="[^"]*">/, `<meta name="twitter:title" content="${esc(titulo)}">`)
      .replace(/<meta name="twitter:description" content="[^"]*">/, `<meta name="twitter:description" content="${esc(desc)}">`)
      .replace(/<meta name="twitter:image" content="[^"]*">/, `<meta name="twitter:image" content="${img}">`)
      .replace('</head>', `<script type="application/ld+json">${JSON.stringify(ld)}</script>\n</head>`)
      .replace('<main id="main"></main>', `<main id="main">${main}</main>`);
    fs.writeFileSync(path.join(ROOT, `obra-${id}.html`), h);
    console.log('obra-' + id + '.html', '|', titulo, '|', desc.length);
  }
}
fs.unlinkSync(tmp); await b.close();
