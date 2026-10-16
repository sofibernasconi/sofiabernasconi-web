# Versión en inglés del sitio con direcciones propias (en.html, en-bio.html, en-obra-<id>.html…)
# y conexión entre idiomas para Google (hreflang). Correr DESPUÉS de tools/build_obras.mjs:
#   node tools/build_obras.mjs && python3 tools/build_idiomas.py
import re, os, glob
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public'))
S = 'https://sofiabernasconi.com'
PAG = {  # archivo ES: (archivo EN, url ES, url EN, título EN, descripción EN)
 'index.html': ('en.html', '/', '/en', 'Sofía Bernasconi — Visual and media artist, New York',
   'Sofía Bernasconi, Chilean visual and media artist in Brooklyn, New York (NYU ITP). Video installation, performance, art and technology: body, territory and machine.'),
 'bio.html': ('en-bio.html', '/bio', '/en-bio', 'Sofía Bernasconi — Bio · Chilean artist in New York',
   'Sofía Bernasconi Le Roy, a Chilean, Latin American woman artist in media arts, based in Brooklyn, New York. Currently at NYU ITP (Tisch School of the Arts).'),
 'proyectos.html': ('en-proyectos.html', '/proyectos', '/en-proyectos', 'Sofía Bernasconi — Projects',
   'Video installation, performance and art and technology works by Sofía Bernasconi, a Chilean Latina media artist based in Brooklyn, New York.'),
 'prensa.html': ('en-prensa.html', '/prensa', '/en-prensa', 'Sofía Bernasconi — Press',
   'Press, interviews and publications about Sofía Bernasconi Le Roy, Chilean visual and media artist.'),
 'contacto.html': ('en-contacto.html', '/contacto', '/en-contacto', 'Sofía Bernasconi — Contact',
   'Contact Sofía Bernasconi Le Roy, Chilean visual and media artist based in Brooklyn, New York.'),
}
SCRIPT = ("<script>/*idioma-fijo*/(function(){var d=document.documentElement,f=d.getAttribute('data-lang'),alt=d.getAttribute('data-alt');"
  "if(!f)return;var q=new URLSearchParams(location.search).get('lang');"
  "if(q&&q!==f&&alt){location.replace(alt+location.hash);return;}"
  "try{localStorage.setItem('lang',f)}catch(e){}"
  "document.addEventListener('click',function(e){var s=e.target.closest&&e.target.closest('#lang span');"
  "if(s&&alt&&s.getAttribute('data-l')!==f){e.preventDefault();e.stopImmediatePropagation();location.href=alt+(location.hash||'');}},true);})();</script>")
OLD = re.compile(r"<script>\(function\(\)\{var l=new URLSearchParams\(location\.search\)\.get\('lang'\);if\(!l\)\{try\{l=localStorage\.getItem\('lang'\)\}catch\(e\)\{\}\}if\(l==='en'\)document\.documentElement\.lang='en';\}\)\(\);</script>\n")

def cabeza(s):
    s = OLD.sub('', s)
    s = re.sub(r"<script>/\*idioma-fijo\*/.*?</script>\n?", '', s, flags=re.S)
    return s.replace('</head>', SCRIPT + '\n</head>', 1)

def alternos(s, ues, uen):
    s = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', '', s)
    return re.sub(r'(<link rel="canonical" href="[^"]*">)',
        r'\1' + f'\n<link rel="alternate" hreflang="es" href="{S}{ues}">\n<link rel="alternate" hreflang="en" href="{S}{uen}">\n<link rel="alternate" hreflang="x-default" href="{S}{ues}">', s, count=1)

def a_ingles(s):
    s = re.sub(r'data-es="([^"]*)" data-en="([^"]*)">\1<', lambda m: f'data-es="{m.group(1)}" data-en="{m.group(2)}">{m.group(2)}<', s)
    s = re.sub(r'href="(bio|proyectos|prensa|contacto)\.html', r'href="en-\1.html', s)
    s = s.replace('href="index.html', 'href="en.html')
    s = re.sub(r'href="obra-([a-z0-9]+)\.html(\?lang=en)?', r'href="en-obra-\1.html', s)
    s = re.sub(r'<body(\s*)>', '<body class="en">', s, count=1)
    s = s.replace('<meta property="og:locale" content="es_CL">\n<meta property="og:locale:alternate" content="en_US">',
                  '<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="es_CL">')
    return s

# páginas principales
for es, (en, ues, uen, tit, desc) in PAG.items():
    s = open(es, encoding='utf-8').read()
    s = re.sub(r'<html[^>]*>', f'<html lang="es" data-lang="es" data-alt="{en}">', s, count=1)
    s = alternos(cabeza(s), ues, uen)
    open(es, 'w', encoding='utf-8').write(s)
    e = re.sub(r'<html[^>]*>', f'<html lang="en" data-lang="en" data-alt="{es}">', s, count=1)
    e = re.sub(r'<title>[^<]*</title>', f'<title>{tit}</title>', e, count=1)
    for k in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
        e = re.sub(r'<meta ' + k + r' content="[^"]*">', f'<meta {k} content="{desc}">', e, count=1)
    for k in ['property="og:title"', 'name="twitter:title"']:
        e = re.sub(r'<meta ' + k + r' content="[^"]*">', f'<meta {k} content="{tit}">', e, count=1)
    e = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{S}{uen}">', e, count=1)
    e = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{S}{uen}">', e, count=1)
    if es == 'index.html':
        e = e.replace('"jobTitle":"Artista visual y artes mediales"', '"jobTitle":"Visual and media artist"')
        e = e.replace('"description":"Artista visual chilena y latinoamericana de artes mediales y nuevos medios, radicada en Brooklyn, Nueva York, y estudiante de ITP en NYU. Trabaja en videoinstalación, performance y arte y tecnología."',
                      '"description":"Chilean, Latin American visual and media artist based in Brooklyn, New York, and a student at NYU ITP. Works in video installation, performance and art and technology."')
        e = e.replace('— artista visual y de artes mediales chilena en Brooklyn, Nueva York</h1>', '— Chilean visual and media artist in Brooklyn, New York</h1>')
        e = e.replace('"url":"https://sofiabernasconi.com"', '"url":"https://sofiabernasconi.com/en"')
        assert '"description":"Artista' not in e and 'Trabaja en' not in e, 'ficha de en.html quedó en español: revisar reemplazos de JSON-LD'
    open(en, 'w', encoding='utf-8').write(a_ingles(e))
    print(es, '->', en)

# obras (ya generadas por build_obras.mjs con data-lang/data-alt y hreflang)
for f in sorted(glob.glob('obra-*.html') + glob.glob('en-obra-*.html')):
    s = cabeza(open(f, encoding='utf-8').read())
    if f.startswith('en-'): s = a_ingles(s)
    open(f, 'w', encoding='utf-8').write(s)
print('obras:', len(glob.glob('obra-*.html')), '+', len(glob.glob('en-obra-*.html')))

# sitemap
ids = [f[5:-5] for f in sorted(glob.glob('obra-*.html'))]
pares = [(v[1], v[2], p) for v, p in zip(PAG.values(), ['1.0','0.8','0.9','0.7','0.6'])] + [(f'/obra-{i}', f'/en-obra-{i}', '0.8') for i in ids]
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
import datetime; hoy = datetime.date.today().isoformat()
for ues, uen, pr in pares:
    for u in (ues, uen):
        out.append(f'  <url><loc>{S}{u}</loc><lastmod>{hoy}</lastmod><priority>{pr}</priority>'
                   f'<xhtml:link rel="alternate" hreflang="es" href="{S}{ues}"/><xhtml:link rel="alternate" hreflang="en" href="{S}{uen}"/>'
                   f'<xhtml:link rel="alternate" hreflang="x-default" href="{S}{ues}"/></url>')
out.append('</urlset>')
open('sitemap.xml', 'w').write('\n'.join(out) + '\n')
print('sitemap:', len(pares) * 2, 'urls')
