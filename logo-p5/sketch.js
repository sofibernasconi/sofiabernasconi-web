// SOFIA BERNASCONI — interactive particle logo (p5.js)
// © 2026 Sofía Bernasconi Le Roy. All rights reserved. See ../LICENSE.
//
// The name, held loosely by a soft spring, floating on a noise field.
// The cursor (or a finger) makes it overflow — desborde — and evaporate;
// then it drifts back, light.
//
// Standalone version of the logo on sofiabernasconi.com.
// Keys:  S = save PNG   ·   R = rebuild   ·   I = invert (light / dark)

// ---------- settings ----------
const FONT = 'Syne';          // typeface (loaded in index.html from Google Fonts)
const TEXT_LINES = ['SOFIA BERNASCONI'];          // desktop: one line
const TEXT_LINES_MOBILE = ['SOFIA', 'BERNASCONI']; // narrow screens: two lines
const R = 160;                // cursor influence radius (px)
const VSTRETCH = 1.55;        // vertical stretch of the name
const DENSITY = 2.4;          // particle spacing (lower = denser, heavier)
let PAPER = [247, 246, 244];  // background
let INK = [21, 21, 15];       // particle colour

// ---------- state ----------
let img, parts = [], nLines = 1, glow;
let x0 = 0, y0 = 0, x1 = 0, y1 = 0;   // name bounding box on screen

function setup() {
  createCanvas(windowWidth, windowHeight);
  pixelDensity(Math.min(2, window.devicePixelRatio || 1));
  glow = createGraphics(width, height);
  glow.pixelDensity(1);
  const boot = () => { img = makeText(); build(); };
  if (document.fonts && document.fonts.load) {
    document.fonts.load('700 120px "' + FONT + '"').then(boot).catch(boot);
  } else boot();
}

function isNarrow() { return width < 700; }

// Render the name in black on white, off-screen, to sample particle positions.
function makeText() {
  const fs = 200;
  const lines = isNarrow() ? TEXT_LINES_MOBILE : TEXT_LINES;
  nLines = lines.length;
  const m = createGraphics(10, 10);
  m.textFont(FONT); m.textStyle(BOLD); m.textSize(fs);
  m.drawingContext.wordSpacing = '75px';
  let tw = 0;
  for (const l of lines) {
    tw = Math.max(tw, Math.ceil(m.textWidth(l)));
  }
  m.remove();
  const pad = 20, lead = fs * 1.04;
  const g = createGraphics(tw + pad * 2, Math.ceil(lead * (nLines - 1) + fs * 1.3));
  g.pixelDensity(1);
  g.background(255); g.fill(0); g.noStroke();
  g.textFont(FONT); g.textStyle(BOLD); g.textSize(fs);
  g.drawingContext.wordSpacing = '75px';
  const multi = nLines > 1;                       // two lines are left-aligned, like on the site
  g.textAlign(multi ? LEFT : CENTER, CENTER);
  const cy = g.height / 2 - lead * (nLines - 1) / 2;
  for (let i = 0; i < lines.length; i++) {
    g.text(lines[i], multi ? pad : g.width / 2, cy + i * lead);
  }
  g.loadPixels();
  return g;
}

function targetW() { return isNarrow() ? width * 0.92 : Math.min(width * 0.72, 900); }

function build() {
  parts = [];
  const s = targetW() / img.width;
  const step = Math.max(2, Math.round((isNarrow() ? 1.8 : DENSITY) / s));
  for (let y = 0; y < img.height; y += step) {
    for (let x = 0; x < img.width; x += step) {
      if (img.pixels[4 * (x + y * img.width)] < 115) {
        parts.push({ ix: x, iy: y, ox: 0, oy: 0, vx: 0, vy: 0, ev: 0,
                     seed: random(1000), sz: random(0.5, 1.15), fst: frameCount + random(0, 85) });
      }
    }
  }
  setHomes();
}

// Place every particle's "home" so the name is centred on screen.
function setHomes() {
  const tw = targetW(), s = tw / img.width, h = img.height * s * VSTRETCH;
  x0 = (width - tw) / 2; y0 = (height - h) / 2; x1 = x0 + tw; y1 = y0 + h;
  for (const q of parts) {
    q.hx = x0 + q.ix * s;
    q.hy = y0 + q.iy * s * VSTRETCH;
    q.hyL = (q.iy % (img.height / nLines)) * s * VSTRETCH; // wave phase per line
  }
}

function draw() {
  background(PAPER);
  glow.clear();
  if (!img) return;

  // pointer: mouse or first touch; off-canvas when not present
  let mx = -999, my = -999;
  if (touches.length) { mx = touches[0].x; my = touches[0].y; }
  else if (mouseX > 0 && mouseY > 0 && mouseX < width && mouseY < height) { mx = mouseX; my = mouseY; }

  const t = frameCount * 0.003, wt = frameCount * 0.01;
  const cX = (x0 + x1) / 2, cY = (y0 + y1) / 2;
  noStroke(); glow.noStroke();

  for (const q of parts) {
    const fade = constrain((frameCount - q.fst) / 28, 0, 1);   // fades in over ~2 s
    const wv = isNarrow() ? q.hyL : q.hy;
    const waveX = (Math.sin(wv * 0.07 - wt * 1.2) * 20 + Math.sin(wv * 0.15 + wt * 0.8) * 8) * (1 - q.ev);
    const baseX = q.hx + waveX, baseY = q.hy;
    const px = baseX + q.ox, py = baseY + q.oy;

    // soft spring back home (weakens while evaporated) + a little noise
    const k = 0.016 * (1 - 0.99 * q.ev);
    let ax = -q.ox * k, ay = -q.oy * k;
    ax += (noise(q.seed, t) - 0.5) * 0.05;

    // the cursor "heats" particles: they evaporate
    const d = Math.hypot(px - mx, py - my);
    if (d < R) q.ev = Math.min(1, q.ev + (1 - d / R) * 0.09);
    if (q.ev > 0.02) {
      const a = noise(px * 0.0016, py * 0.0016, t * 0.4) * TWO_PI * 2;  // flow field
      const drift = 0.5 * q.ev;
      ax += Math.cos(a) * drift + (px - cX) * 0.00075 * q.ev;
      ay += Math.sin(a) * drift + (py - cY) * 0.00075 * q.ev;
    }
    q.ev *= 0.991;                                       // cools down slowly

    const fr = 0.92 + 0.05 * q.ev;
    q.vx = (q.vx + ax) * fr; q.vy = (q.vy + ay) * fr;
    const sp = Math.hypot(q.vx, q.vy), cap = 3.2;
    if (sp > cap) { q.vx *= cap / sp; q.vy *= cap / sp; }
    q.ox += q.vx; q.oy += q.vy;

    const dx = baseX + q.ox, dy = baseY + q.oy;
    const dot = q.sz * 1.5 * (isNarrow() ? 0.7 : 1);
    const aC = 255 * (1 - q.ev) * fade;
    if (aC > 4) { fill(INK[0], INK[1], INK[2], aC); circle(dx, dy, dot); }
    if (q.ev > 0.03) { glow.fill(INK[0], INK[1], INK[2], 150 * q.ev * fade); glow.circle(dx, dy, dot + q.ev * 3); }
  }

  // evaporated particles become a blurred mist
  drawingContext.filter = 'blur(2.6px)';
  image(glow, 0, 0, width, height);
  drawingContext.filter = 'none';
}

function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('sofia-bernasconi-logo', 'png');
  if (key === 'r' || key === 'R') build();
  if (key === 'i' || key === 'I') { [PAPER, INK] = [INK, PAPER]; }
}

function touchMoved() { return false; } // keep the page from scrolling while drawing

let resizeTimer;
function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  glow.resizeCanvas(windowWidth, windowHeight);
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => { if (img) { img = makeText(); build(); } }, 150);
}
