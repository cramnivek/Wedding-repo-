# wedding

The wedding site for Marc-Kevin & Florence — 6 October 2026, five o'clock in the
evening, reception at Smoque Bistro, Tagbilaran City, Bohol.

One file, no build step, no dependencies. `index.html` is the whole site. Open it
in a browser to see it; edit it in any text editor to change it.

---

## Design

Taken from the printed invitation rather than invented: black ground, Calla Green
silk, Merlot and burgundy blooms, white script names.

| Role | Value |
| --- | --- |
| Ground | `#050505` |
| Silk / accent | `#7C8447` — close to Pantone 18-0435 TCX Calla Green |
| Merlot | `#74303C` — Pantone 19-1534 TCX |
| Burgundy | `#8C1F3A` |
| Bloom (petals) | `#C9382B` |

Typefaces, from Google Fonts: **Allura** for the names and monogram (an
approximation of the invitation's calligraphy, not the same file), **Cormorant
Garamond** for headings and italic asides, **Montserrat** for the letterspaced
caps and body. If they fail to load the page falls back to system serif and sans
and still reads correctly.

The green silk and the drifting petals are drawn on `<canvas>` at runtime — there
are no image files in this repo.

## What is still blank

Details we don't have yet are wrapped in `<span class="slot">` and show as sage
text with a dashed underline. Search the file for `class="slot"` to find them all.
Replace the text inside each one; you can then drop the `class="slot"` attribute
so the dashed underline goes away.

Outstanding:

- **The ceremony venue** — the invitation only names the reception
- **Five of the six times** in the order of the day; only 5:00 is real
- **Reply-by date** and **your email address**
- Parking, travel from the airport or pier, hotels
- Children, plus-ones, gifts, photographs

Two places hold the email and must match: the `.slot` in the RSVP note, and the
`TO` variable near the bottom of the `<script>` block.

```js
var TO = "your@email";
```

The date lives in one place — the `data-` attributes on `.stack`. The countdown
and the Google Calendar link both read from there, so they can't disagree.

```html
<div class="stack"
     data-when="2026-10-06T17:00"
     data-ends="2026-10-06T23:00"
     data-title="Wedding of Marc-Kevin &amp; Florence"
     data-where="Smoque Bistro, Carlos P. Garcia East Avenue, Tagbilaran City, Bohol">
```

## How RSVPs work right now

There is no backend. When a guest submits the form, the page composes a
plain-text reply, shows it to them, and hands it to their own email app via a
`mailto:` link. Nothing can be silently lost, but replies arrive as individual
emails rather than as a list.

To collect them properly, pick one:

- **Google Form** — free. Delete the `<form>` and point the RSVP button at your
  form instead. Answers land in a spreadsheet.
- **Netlify Forms** — free tier, ~100 submissions a month, only if you host on
  Netlify. Add `netlify` and `name="rsvp"` to the `<form>` tag and remove the
  submit handler.
- **Formspree** — works on any host, free tier ~50 a month. Set the form's
  `action` to your Formspree endpoint and `method="POST"`.

## Interaction

- Live countdown to five o'clock on the sixth, ticking every second
- Scroll-driven reveals using native `animation-timeline: view()`, wrapped in
  `@supports` so browsers without it render everything at rest
- The invitation leans toward the pointer; the silk sways with it
- QR code of whatever URL the page is served from — print it on stationery
- Add-to-calendar as a Google Calendar link, which opens on any device
- The RSVP folds away party size, diet and song on a decline

Everything motion-related switches off under `prefers-reduced-motion`. The silk
is still drawn, just held still.

## Publishing it

The site is static, so anything that serves files will do.

- **Netlify / Vercel / Cloudflare Pages** — drag the folder onto their dashboard.
  Free, custom domain supported, done in a minute.
- **GitHub Pages** — Settings → Pages → deploy from `main`, root folder.
  Note that Pages sites are public even when the repository is private.
