# wedding

The wedding site for Marc-Kevin & Florence — 6 October 2026, five o'clock in the
evening, reception at Smoque Bistro, Tagbilaran City, Bohol.

One file, no build step, no dependencies. `index.html` is the whole site. Open it
in a browser to see it; edit it in any text editor to change it.

---

## Design

Burgundy and black from the printed invitation, lit the way *Shadow of the
Erdtree* lights its key art: a near-black ground, gold falling out of an eclipse,
and almost no colour that isn't ember, bone or blood.

| Role | Token | Value |
| --- | --- | --- |
| Ground | `--ink` | `#0A0806` |
| Panel | `--panel` | `#0D0A07` |
| Text | `--bone` | `#EBDCC0` |
| Text, secondary | `--bone-soft` | `#C4B296` |
| Text, muted | `--muted` | `#9C8B70` — 6.04:1 on `--ink` |
| Blood | `--blood` | `#8E1119` |
| Ember | `--ember` | `#E8A23A` |
| Gold | `--gold` | `#D9A441` |

Every text token clears WCAG AA on the ground it sits on. `--blood-lt` (`#C21F26`)
is only ever a border or a list marker, never text.

Typefaces, from Google Fonts: **Allura** for the monogram and the gate card,
**Cinzel** for every heading and letterspaced cap, **Cormorant Garamond** for
body text. If they fail to load the page falls back to system serif and sans and
still reads correctly.

The eclipse, its corona, the light falling from it, the fog and the dead branches
are all drawn on `<canvas>` at runtime. The twelve plates in `img/` are the only
image files, and `place.py` is what grades them — it maps each one's luminance
through the page's own palette ramp, so a render made in any light still belongs
here.

## What is still blank

Details we don't have yet are wrapped in `<span class="slot">` and show as rose
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
