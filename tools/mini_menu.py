"""Adds the mini menu (three small bars, top right) to every page in public/.

When the visitor scrolls down, the full menu (ES/EN + links) folds into three
short bars in the top-right corner instead of disappearing. Tapping the bars
opens the menu again; tapping again, a link, outside, Esc, or scrolling closes it.
Scrolling back up brings the full menu back, as before.

Run again after rebuilding pages (it replaces the old block, never duplicates it):
    python3 tools/mini_menu.py
"""
import pathlib, re

PUBLIC = pathlib.Path(__file__).resolve().parent.parent / 'public'
MARK_START, MARK_END = '<!--MINI-MENU-->', '<!--/MINI-MENU-->'

BLOCK = MARK_START + r'''
<style>
  #mm{position:fixed;top:26px;right:26px;z-index:125;width:40px;height:34px;padding:0;margin:0;border:0;background:none;cursor:pointer;
      display:flex;flex-direction:column;align-items:flex-end;justify-content:center;gap:5px;padding-right:10px;
      mix-blend-mode:difference;opacity:0;transform:scale(.6);transform-origin:top right;pointer-events:none;
      transition:opacity .5s ease,transform .5s ease;-webkit-tap-highlight-color:transparent}
  #mm i{display:block;width:18px;height:1.5px;background:#fff;border-radius:1px;transition:transform .35s ease,opacity .25s ease,width .35s ease}
  #mm i:nth-child(2){width:12px}
  #mm:hover i:nth-child(2){width:18px}
  body.ui-hide #mm{opacity:1;transform:none;pointer-events:auto}
  /* abierto: las barritas se vuelven una X y el menú vuelve a aparecer */
  body.mm-open #mm i:nth-child(1){transform:translateY(6.5px) rotate(45deg)}
  body.mm-open #mm i:nth-child(2){opacity:0}
  body.mm-open #mm i:nth-child(3){transform:translateY(-6.5px) rotate(-45deg)}
  body.ui-hide.mm-open nav,body.ui-hide.mm-open #menu{opacity:1 !important;transform:none;pointer-events:auto}
  body.ui-hide.mm-open #lang{opacity:1 !important;pointer-events:auto;right:76px}
  /* en la portada el menú es negro: al abrirlo sobre fotos, que se lea igual que en las otras páginas */
  body.ui-hide.mm-open #menu,body.ui-hide.mm-open #lang{mix-blend-mode:difference;color:#fff}
  body.ui-hide.mm-open #menu a{color:#fff}
  @media(max-width:700px){ #mm{top:22px;right:18px} body.ui-hide.mm-open #lang{right:66px} }
</style>
<button id="mm" type="button" aria-expanded="false"><i></i><i></i><i></i></button>
<script>(function(){
  var b=document.getElementById('mm'), B=document.body; if(!b) return;
  var en=(document.documentElement.lang||'').indexOf('en')===0;
  b.setAttribute('aria-label', en?'Menu':'Menú');
  function st(){return window.pageYOffset||document.documentElement.scrollTop||B.scrollTop||0;}
  var y0=0;
  function set(o){ B.classList.toggle('mm-open',o); b.setAttribute('aria-expanded',o?'true':'false'); if(o) y0=st(); }
  b.addEventListener('click',function(e){ e.stopPropagation(); set(!B.classList.contains('mm-open')); });
  document.addEventListener('click',function(e){
    if(!B.classList.contains('mm-open')) return;
    if(e.target.closest && e.target.closest('nav,#menu,#lang,#mm')) return;
    set(false);
  });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') set(false); });
  function sc(){
    if(!B.classList.contains('ui-hide')){ if(B.classList.contains('mm-open')) set(false); return; }
    if(B.classList.contains('mm-open') && Math.abs(st()-y0)>80) set(false);
  }
  window.addEventListener('scroll',sc,{passive:true,capture:true});
  document.addEventListener('scroll',sc,{passive:true,capture:true});
})();</script>
''' + MARK_END + '\n'

pat = re.compile(re.escape(MARK_START) + r'.*?' + re.escape(MARK_END) + r'\n?', re.S)
n = 0
for f in sorted(PUBLIC.glob('*.html')):
    s = f.read_text(encoding='utf-8')
    if '<!--UI-HIDE-ON-SCROLL-->' not in s:
        continue
    s = pat.sub('', s)
    s = s.replace('<!--UI-HIDE-ON-SCROLL-->', BLOCK + '<!--UI-HIDE-ON-SCROLL-->', 1)
    f.write_text(s, encoding='utf-8')
    n += 1
print(f'mini menu added to {n} pages')
