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

Typefaces: **Diablo Heavy** for the names, self-hosted from `fonts/` (see the
note in there — it is a 1997 fan face, not the games' own Exocet). From Google
Fonts: **Cinzel** for every heading and letterspaced cap, **Cormorant Garamond**
for body text, **Allura** for the footer monogram.

The display face is used for the names and nothing else. It has no true
lowercase — lowercase input selects alternate capital forms, which is what puts
the slashed `O` in FLORENCE — so it cannot set a heading, a label or a line of
body text. If any font fails to load the page falls back to system serif and
still reads correctly.

The eclipse, its corona, the light falling from it, the fog, the dead branches
and the whole opening gate are all drawn on `<canvas>` at runtime.

Everything else in `img/` is a file:

- **Fifteen plates**, each in `.avif`, `.webp` and `.jpg` — the page offers all
  three through `<picture>` and the browser takes the first it understands.
  `place.py` grades them: it maps each one's luminance through the page's own
  palette ramp, so a render made in any light still belongs here. The `longest`
  column in its `JOBS` table is a *measured* number — twice the widest the page
  ever renders that plate, read off the layout by `check/maxsize.cjs` — so
  re-running the script after a layout change is what keeps the plates the right
  size rather than three times too big.
- **Four assets that are not plates.** `behelit.webp`, `field.webp` and
  `bloom.webp` are sprite sheets, blitted frame by frame on canvas so the gate
  owns their timing — a GIF plays on its own clock and cannot be told to wait
  for the seal to break. `brand.webp` is the Brand of Sacrifice, cut off its own
  ground by how red each pixel is.
- **`og.jpg`** — the 1200×630 card a messaging app shows when the link is pasted.
- **`chamber.mp4` / `chamber.webm`** — the chamber portrait as a ten-second shot,
  325 and 414 KB. The page plays it in place of that plate; only one of the two
  is ever fetched, the browser picks by codec. See below.
- **`rescue.mp4` / `rescue.webm`** — a second clip, ~360 KB each, **not served
  by the page**: its likenesses didn't survive being animated. Kept because the
  machinery to play it is still there and one attribute switches it on.
- The two favicons and `icon-512.png`.

Cold load is about **1.3 MB over 22 requests**; `check/weigh.cjs` measures it.
If that number climbs a long way, something went in at full size. The video is
not in that figure — it is only fetched on scrolling to it, and adds ~360 KB
for a guest who gets that far.

## What is still blank

Details we don't have yet are wrapped in `<span class="slot">` and show as rose
text with a dashed underline. Search the file for `class="slot"` to find them all.
Replace the text inside each one; you can then drop the `class="slot"` attribute
so the dashed underline goes away.

Outstanding:

- **The ceremony venue** — the invitation only names the reception
- **Five of the six times** in the order of the day; only 5:00 is real
- **Reply-by date**
- Parking at the venue, and whether a room block is held anywhere

Travel is filled in from public sources: the airport transfer, the Cebu ferry,
named hotels in Tagbilaran and what October weather does. Fares and schedules
drift — worth a check closer to the date.

The contact address is filled in — `marcarlinghaus@gmail.com`. It lives in three
places that must agree, so change all three together: the RSVP note, the footer's
`mailto:` link, and the `TO` variable near the bottom of the `<script>` block.

```js
var TO = "marcarlinghaus@gmail.com";
```

The date lives in one place — the `data-` attributes on `.stack`. The countdown
and the Google Calendar link both read from there, so they can't disagree. The
`+08:00` is load-bearing: without it the time is parsed in whatever zone the
visitor's browser is in, and a guest abroad gets a countdown and a calendar entry
several hours out.

```html
<div class="stack"
     data-when="2026-10-06T17:00+08:00"
     data-ends="2026-10-06T23:00+08:00"
     data-title="Wedding of Marc-Kevin &amp; Florence"
     data-where="Smoque Bistro, Carlos P. Garcia East Avenue, Bool, Tagbilaran City, Bohol">
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
- The invitation leans toward the pointer
- Add-to-calendar as a Google Calendar link, which opens on any device
- The RSVP folds away party size, diet and song on a decline

Before any of that there is a gate: an invitation drawn as a manga page, inked
in front of you, sealed in wax and branded. Pressing the brand breaks the seal,
the ink runs, the envelope tears, and the tear opens into the eclipse.

## Plates that move

Any `<figure>` carrying `data-clip` plays a clip in place of the still inside
it. The attribute names the file **without an extension** — the script appends
one per source type. One plate uses it today: the chamber portrait in the
prenup pair.

The still stays in the markup and stays the fallback. The video is built in
script and only swapped in once it has decoded a frame, so script off, reduced
motion, a missing file or a browser that won't decode it all leave exactly the
page that was there before — never a black rectangle where a plate used to be.

Nothing downloads until the gate has been opened *and* the plate is near, so a
clip never competes with the gate and a guest who doesn't scroll that far never
pays for it. Cold load is unchanged at 1.33 MB. Each clip plays once and holds
on its last frame rather than looping; clicking it plays it again.

Two encodings are published because "every browser plays mp4" is not true: a
Chromium built without the proprietary codecs decodes neither H.264 nor the
reason it failed. Each `<source>` names its codec, not just its container —
given only `video/mp4` a browser answers "maybe" on the container alone, fetches
the whole file, then discovers it can't play it and fetches the other one too.

### Which stills survive being animated, and why

Three attempts, and the thing that decided them was **how many pixels the faces
occupy in the source**, not anything about the prompt.

The rescue still was animated twice — once with a push-in, once with the camera
locked off. Both came back with a stranger's face. In that plate their faces are
about 70px across, which is not enough identity for the generator to preserve,
so it invents the rest and invents someone else. Holding the camera still didn't
help; it only made the wrong face consistent for ten seconds instead of
drifting. Frame one is already re-rendered, before any camera move has happened.

The chamber portrait works because the faces are around 250px, with glasses, a
neck tattoo and a nose piercing to hold on to. That one is on the page.

So: animate the tightest plate you have, not the best-composed one. And keep the
motion small — breath, a blink, firelight, drifting dust. Asking for a camera
move is asking the model to invent pixels it doesn't have.

### Replacing or adding a clip

Encode to both formats at the same base name, and keep the `avc1.…` string in
the page matching what the mp4 actually contains (read it from the file's `avcC`
box if you're unsure). Crop to the shape the plate renders at rather than
letting the browser throw pixels away — the chamber cell is square and never
wider than 374 CSS px, so the clip is 720×720:

```sh
ffmpeg -i in.mp4 -an -vf crop=720:720:230:0 -c:v libx264 -crf 30 \
  -pix_fmt yuv420p -movflags +faststart img/chamber.mp4
ffmpeg -i in.mp4 -an -vf crop=720:720:230:0 -c:v libvpx-vp9 -crf 48 -b:v 0 \
  img/chamber.webm
```

Grade it the same way `place.py` grades the still it replaces, or the colour
visibly shifts at the moment it swaps in. `place.py` exposes `to_palette`, so
the frames can go through the identical ramp:

```py
im = place.to_palette(im, KEEP)                      # chamber: 0.58
im = ImageEnhance.Contrast(im).enhance(CONTRAST)     # 1.10
im = ImageEnhance.Brightness(im).enhance(BRIGHT)     # 0.94
```

`art-source/` holds the full-size versions with their sound, watermark removed,
for sending to people rather than serving.

Breaking the seal also plays a sound, synthesised in the browser rather than
loaded — a file cannot follow the gate, and this is built off the same timeline
the animation is, so it arrives at silence exactly when the page does. The
toggle in the corner remembers its setting, and it starts off for anyone who has
asked their system for less motion.

Everything motion-related switches off under `prefers-reduced-motion` — the gate
removes itself outright rather than playing at a lower speed.

## The printed card

`card/` is a separate one-page file: a 5 × 7in save-the-date, front and back,
laid out in millimetres with trim, bleed and safe margins. Open it, print to PDF
from the browser, and read the notes underneath it before sending it anywhere —
they cover the two things that ruin a dark card at a press. The site address on
the back is still blank.

## Checking it still works

`check/` holds the regression scripts, one concern each. They drive a real
browser over `../index.html`, so they catch things a glance at the page does not
— a countdown that is right in your timezone and wrong in everyone else's, a
phone laying the page out at 980px, a band 156px wider than the screen.

```sh
cd check
npm install            # playwright-core only
npm run all            # or: gate, overflow, timezone, sound, viewport, clip, weight, contrast
```

Chromium comes from wherever Playwright finds it, or set `CHROME_PATH` to one
you already have. `check/README.md` says what each script is for and what it
caught.

## Publishing it

The site is static, so anything that serves files will do.

- **Netlify / Vercel / Cloudflare Pages** — drag the folder onto their dashboard.
  Free, custom domain supported, done in a minute.
- **GitHub Pages** — Settings → Pages → deploy from `main`, root folder.
  Note that Pages sites are public even when the repository is private.

**One thing to change the day it gets a domain.** `og:image` in the `<head>` is
a relative path, `img/og.jpg`. Some crawlers resolve that against the page URL
and some silently ignore it — Facebook's among the latter — so the link preview
will work in one app and come up blank in another. Make it absolute:

```html
<meta property="og:image" content="https://your-domain/img/og.jpg">
```
