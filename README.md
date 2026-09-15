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
- **Four plates that move**, each as an mp4 and a webm — `vow`, `camp`, `ridge`
  and `chamber`. Only one of the two is ever fetched per clip; the browser picks
  by codec. mp4 242/508/358/325 KB, webm 271/716/429/414 KB. See below.
- **`rescue.mp4` / `rescue.webm`** — a fifth clip, ~360 KB each, **not served
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
one per source type. Four plates use it, all in the prenup: `vow`, `camp`,
`ridge` and `chamber`.

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

### Adding a clip

`clip.py` does the whole thing. It crops and scales to the size that plate is
actually rendered at, grades every frame through `place.py`'s ramp using that
plate's own row from `JOBS`, and writes both encodings:

```sh
python3 clip.py chamber incoming/chamber.mp4 --crop 720:720:230:0
```

Then add `data-clip="img/chamber"` to that plate's `<figure>` and run
`check/clip.cjs`. The script prints the mp4's real `avc1.…` string; if it
differs from the one in the page's `<source type>`, change the page.

Three things it is doing that are easy to skip and shouldn't be:

- **Cropping to the rendered shape**, not shipping the generator's framing. The
  chamber cell is square and never wider than 374 CSS px, so its clip is
  720×720 — the 44% the browser would have discarded is never encoded.
- **Grading with the still's own settings.** An ungraded clip swapping in for a
  graded picture shifts colour visibly at the moment of the swap.
- **Never upscaling.** A crop smaller than the target is left alone; enlarging
  it invents nothing and costs bytes.

`--delogo` paints out the generator's watermark, at the fixed position in
`WATERMARK`. It is usually unnecessary: a crop that matches the plate's shape
tends to exclude the corner it sits in anyway.

**Check the result by eye, not by pixel count.** `delogo` interpolates from the
edges of its box, which is invisible on smooth dark ground and leaves an obvious
blurred rectangle on texture — it did exactly that on `ridge`, whose corner is
burned rubble. A count of surviving bright pixels reported zero and was no help.
Where it smears, clone instead: the camera is locked off, so one patch cloned
from beside the mark, feathered, works on every frame.

`art-source/` holds the full-size versions with their sound, watermark removed,
for sending to people rather than serving — one `<plate>-clip.mp4` per clip.

### What it costs on a phone

Measured by `check/phone.cjs` at 390px with `isMobile` on, which is the only
configuration that tells the truth about this:

| | |
| --- | --- |
| Cold, gate opened, before any scrolling | **1.01 MB** over 18 requests |
| After scrolling the whole page | **3.4 MB** over 32 requests |
| …of which video | **1.8 MB** (1.4 MB on Safari, which takes the mp4) |
| …of which fonts | **214 KB** across 7 faces |

Of that cold megabyte, **415 KB is the gate** — the Behelit, eruption and field
sprites plus the Brand. That is what the opening costs, paid before anything
else, and it is the largest single thing left if the number ever has to come
down.

Note the fonts are in the cold figure now that they are served from here. They
were always being fetched; they used to come from Google and so never appeared
in a local measurement.

**Anyone with Data Saver on, or on a 2G-class connection, gets no video at
all** — the stills stay and nothing is fetched, verified in `phone.cjs`. Safari
exposes neither signal, so that is a courtesy where it works rather than a
guarantee.

Four clips is the ceiling. The ones worth spending it on are where motion says
something a still can't: firelight moving across a face, wind in a cloak,
someone's eyes opening. If another is added, take one of these off.

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

## Putting it on a domain

**The repository is not the website.** `art-source/` alone is 70 MB of ungraded
originals and full-size clips — nine times the size of the site — and `check/`,
`place.py` and `clip.py` are tooling. `build.sh` assembles the 8.7 MB that
guests actually need into `dist/`, and that is what gets published.

```sh
sh build.sh
```

The address is **marcandflo.com**, registered through Cloudflare. `build.sh`
defaults to it and writes it into the two places that cannot be relative: the
`og:image` URL, without which a pasted link previews in some apps and comes up
blank in others, and the site address on the back of the printed card. Pass a
different URL to point it elsewhere, or `""` to leave both blank.

### The steps

The domain is already at Cloudflare, so **Cloudflare Pages** is the path of
least resistance — the DNS is in the same account and a custom domain is a
couple of clicks with nothing to edit by hand. It also has a point of presence
in Manila, so for guests in Bohol the files come from inside the country rather
than from Singapore or the US. On a site nobody loads twice, that first visit is
the whole experience.

1. **Workers & Pages → Create → Pages → Connect to Git**, and pick
   `cramnivek/wedding-repo-`.
2. Set the build:
   - framework preset: **None**
   - build command: `sh build.sh`
   - output directory: `dist`
3. Deploy. It will come up on a `*.pages.dev` URL first — open that and check it
   before pointing the domain at it.
4. **Custom domains → Set up a domain → `marcandflo.com`.** Cloudflare adds the
   DNS record itself and issues the certificate. Add `www` too if you want it to
   work either way.
5. **Paste the link into a message to yourself** and confirm the preview card
   shows the eclipse and your names rather than a bare URL.

After that every push to `main` redeploys on its own.

**GitHub Pages would work too**, but it deploys the repository as-is with no
build step, which would publish all 70 MB of `art-source/` — and Pages sites are
public even when the repository is private.

### What the host needs to do, and what it does for free

`_headers` (Netlify, Cloudflare Pages) and `vercel.json` (Vercel) carry the
cache rules, and `build.sh` copies `_headers` into `dist/` because both hosts
read it from the published directory rather than the repository root.

Nothing here is content-hashed — `img/chamber.mp4` keeps that name when it is
replaced — so the plates and clips get a week rather than the year an immutable
asset would, with `stale-while-revalidate` so a returning guest renders straight
from cache. `index.html` must revalidate every time, or an edit to a venue or a
time sits behind a stale copy on every phone that has already opened it.

Compression you get for nothing: `index.html` is 119 KB and **gzips to 34 KB**,
and every one of these hosts serves Brotli, which does better still. The images
and video are already compressed and are not touched.
