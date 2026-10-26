# Interactive logo — p5.js

Standalone version of the particle logo used on [sofiabernasconi.com](https://sofiabernasconi.com).

The name is made of particles held loosely by a soft spring, floating on a noise field. The cursor (or a finger on touch screens) makes it overflow — *desborde* — and evaporate into a blurred mist; then it slowly drifts back.

## Run it

- **Locally:** open `index.html` in a browser (an internet connection is needed to load p5.js and the Syne font).
- **p5.js Web Editor:** create a new sketch, paste `sketch.js`, and add this line to the editor's `index.html` `<head>`:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap" rel="stylesheet">
  ```

## Controls

| Key | Action |
|-----|--------|
| Mouse / touch | Evaporate the name |
| `S` | Save a PNG |
| `R` | Rebuild the particles |
| `I` | Invert colours (light / dark) |

Settings (font, text, cursor radius, density, colours) are at the top of `sketch.js`. Set `MIST = true` to make evaporated particles leave a blurred, enlarged trail (off by default, matching the website).

---

© 2026 Sofía Bernasconi Le Roy. All rights reserved. The logo, its design and this code may not be copied, modified or reused without permission — see [LICENSE](../LICENSE).
