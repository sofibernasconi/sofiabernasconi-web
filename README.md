# sofiabernasconi.com

Website of **Sofía Bernasconi Le Roy**, Chilean visual and media artist based in New York.
Video installation, performance, kinetic installation and art & technology — body, territory and machine.

🌐 [sofiabernasconi.com](https://sofiabernasconi.com) · 🇬🇧 [English version](https://sofiabernasconi.com/en) · 📷 [@sofibernasconi](https://www.instagram.com/sofibernasconi/)

---

## How it works

A static site (HTML, CSS and vanilla JavaScript, with [p5.js](https://p5js.org) for the interactive logo), hosted on **Cloudflare Workers**.
Every push to `main` is deployed automatically — whatever is in `public/` goes live.

## Structure

```
public/                  The website (everything here is published)
├── index.html, en.html          Home (Spanish / English)
├── bio, proyectos, prensa, contacto (.html)   Main pages — en-*.html are the English versions
├── obra.html                    Template for artwork pages
├── obra-<id>.html               Artwork pages, generated from obra.html (en-obra-<id>.html in English)
├── assets/                      Photos, logos, icons; assets/prensa/ holds press clippings
├── sitemap.xml, robots.txt      For search engines
├── _redirects                   301 redirects from the old WordPress site
└── _headers                     Extra HTTP headers (e.g. images hidden from Google Images)

tools/                   Build scripts (not published)
├── build_obras.mjs              obra.html → one page per artwork, ES + EN
├── build_idiomas.py             English pages, hreflang links and sitemap
├── build_alts.py                Photo alt text, image sitemap and video structured data
├── mini_menu.py                 Menu that folds into three small bars when scrolling (all pages)
├── alts.json                    Alt text for every photo (ES / EN)
├── videos.json                  YouTube videos per artwork
└── renombre_fotos.json          Old → new photo filenames (kept for reference)

logo-p5/                 Standalone p5.js version of the interactive logo (not published)
drafts/                  Intro/logo experiments and backup photos (not published)
wrangler.jsonc           Cloudflare configuration
```

## Editing

- **Text or images on a page:** edit the file in `public/` and push to `main`.
- **An artwork:** edit `public/obra.html`, then rebuild all generated pages, in this order:
  ```bash
  node tools/build_obras.mjs        # needs Playwright: npm i playwright && npx playwright install chromium
  python3 tools/build_idiomas.py
  python3 tools/build_alts.py
  python3 tools/mini_menu.py       # re-adds the mini menu (bars on scroll) to every page
  ```
- **Preview locally:** `npx wrangler dev`, or open the HTML files directly in a browser.

Pages are bilingual: Spanish is the default and the English versions live at their own URLs (`/en`, `/en-bio`, `/en-obra-<id>`…).

## Copyright

© 2018–2026 Sofía Bernasconi Le Roy. **All rights reserved.**

All artworks, images, texts, the logo, the design and the code in this repository are the artist's property. This repository is public so the site can be deployed and viewed — it is **not** open source. Nothing here may be copied, reused or redistributed without written permission. Press clippings and partner logos belong to their respective owners.

See [LICENSE](LICENSE) for details. Permission requests: [contacto@sofiabernasconi.com](mailto:contacto@sofiabernasconi.com).
