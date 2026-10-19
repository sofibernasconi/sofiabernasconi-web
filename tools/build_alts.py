#!/usr/bin/env python3
"""Aplica las descripciones de fotos (tools/alts.json) a todo el sitio.

- Reemplaza el alt de cada <img src="assets/…"> según el idioma de la página (data-lang).
- En obra.html y en las páginas de obra (obra-*.html, en-obra-*.html) deja la tabla
  FOTO_ALT en el script, para que las fotos que dibuja JavaScript usen la misma descripción.
- Agrega las fotos de cada página al sitemap (image:image), para Google Imágenes.

Correr después de build_obras.mjs y build_idiomas.py:
    python3 tools/build_alts.py
"""
import json, re, pathlib, html

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PUB = RAIZ / 'public'
SITIO = 'https://sofiabernasconi.com'
ALTS = {k: v for k, v in json.loads((RAIZ / 'tools' / 'alts.json').read_text('utf8')).items() if not k.startswith('_')}

IMG = re.compile(r'<img\b[^>]*>')
SRC = re.compile(r'\bsrc="assets/([^"/]+)"')
ALT = re.compile(r'\balt="[^"]*"')


def idioma(txt):
    m = re.search(r'<html[^>]*\bdata-lang="(\w+)"', txt)
    return m.group(1) if m else 'es'


def poner_alts(txt, lang):
    def f(m):
        tag = m.group(0)
        s = SRC.search(tag)
        if not s or s.group(1) not in ALTS:
            return tag
        alt = 'alt="' + html.escape(ALTS[s.group(1)][lang], quote=True) + '"'
        return ALT.sub(alt, tag, 1) if ALT.search(tag) else tag.replace('<img', '<img ' + alt, 1)
    return IMG.sub(f, txt)


JS_TABLA = 'const FOTO_ALT = ' + json.dumps(ALTS, ensure_ascii=False) + ';\n'
JS_ALTOF = ("function altOf(id,i,total,f){ var L=(typeof currentLang!=='undefined'&&currentLang==='en')?'en':'es';"
            " if(f&&FOTO_ALT[f]) return FOTO_ALT[f][L];"
            " var b=ALT[id]||(OBRAS[id]?OBRAS[id].title:''); return total>1 ? b+' ('+i+' de '+total+')' : b; }")
LLAMADAS = [
    ("altOf(id,1,1)", "altOf(id,1,1,o.fotos[0])"),
    ("altOf(id,galeria.indexOf(f)+1,galeria.length)", "altOf(id,galeria.indexOf(f)+1,galeria.length,f)"),
    ("altOf(id,i+1,o.slider.length)", "altOf(id,i+1,o.slider.length,f)"),
]


def poner_js(txt):
    txt = re.sub(r'const FOTO_ALT = .*?;\n', '', txt)
    txt = re.sub(r'function altOf\(id,i,total(?:,f)?\)\{.*?\n', lambda m: JS_TABLA + JS_ALTOF + '\n', txt, count=1)
    for a, b in LLAMADAS:
        txt = txt.replace(a, b)
    return txt


VIDEOS = {k: v for k, v in json.loads((RAIZ / 'tools' / 'videos.json').read_text('utf8')).items() if not k.startswith('_')}
LD_VIDEO = re.compile(r'<script type="application/ld\+json" id="ld-video">.*?</script>\n?', re.S)


def poner_videos(txt, nombre, lang):
    """Ficha VideoObject para los videos de YouTube de la obra (Google Videos)."""
    txt = LD_VIDEO.sub('', txt)
    m = re.match(r'(?:en-)?obra-([a-z0-9]+)\.html$', nombre)
    if not m or m.group(1) not in VIDEOS:
        return txt
    url = SITIO + '/' + nombre[:-5]
    items = []
    for v in VIDEOS[m.group(1)]:
        titulo, desc = v[lang]
        items.append({"@type": "VideoObject", "name": titulo, "description": desc,
                      "thumbnailUrl": f"https://i.ytimg.com/vi/{v['yt']}/hqdefault.jpg",
                      "uploadDate": v['fecha'], "embedUrl": f"https://www.youtube.com/embed/{v['yt']}",
                      "url": f"https://www.youtube.com/watch?v={v['yt']}", "inLanguage": lang,
                      "creator": {"@type": "Person", "name": "Sofía Bernasconi", "url": SITIO},
                      "isPartOf": {"@type": "WebPage", "@id": url}})
    data = {"@context": "https://schema.org", "@graph": items} if len(items) > 1 else dict({"@context": "https://schema.org"}, **items[0])
    tag = '<script type="application/ld+json" id="ld-video">' + json.dumps(data, ensure_ascii=False) + '</script>\n'
    return txt.replace('</head>', tag + '</head>', 1)


def main():
    for p in sorted(PUB.glob('*.html')):
        txt = p.read_text('utf8')
        nuevo = poner_alts(txt, idioma(txt))
        if p.name == 'obra.html' or p.name.startswith(('obra-', 'en-obra-')):
            nuevo = poner_js(nuevo)
        if p.name.startswith(('obra-', 'en-obra-')):
            nuevo = poner_videos(nuevo, p.name, idioma(txt))
        if nuevo != txt:
            p.write_text(nuevo, 'utf8')
            print('alts:', p.name)

    # sitemap de imágenes
    sm = PUB / 'sitemap.xml'
    x = sm.read_text('utf8')
    x = re.sub(r'\s*<image:image>.*?</image:image>', '', x, flags=re.S)
    if 'xmlns:image=' not in x:
        x = x.replace('<urlset ', '<urlset xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" ', 1)

    def con_fotos(m):
        bloque = m.group(0)
        loc = re.search(r'<loc>([^<]+)</loc>', bloque).group(1)
        ruta = loc[len(SITIO):].strip('/') or 'index'
        f = PUB / (ruta + '.html')
        if not f.exists():
            return bloque
        fotos = []
        for s in SRC.finditer(f.read_text('utf8')):
            n = s.group(1)
            if n in ALTS and not n.startswith('logo_') and n not in fotos:
                fotos.append(n)
        extra = ''.join(f'\n    <image:image><image:loc>{SITIO}/assets/{n}</image:loc></image:image>' for n in fotos)
        return bloque.replace('</url>', extra + '\n  </url>')

    x = re.sub(r'<url>.*?</url>', con_fotos, x, flags=re.S)
    sm.write_text(x, 'utf8')
    print('sitemap: imágenes', x.count('<image:image>'))


if __name__ == '__main__':
    main()
