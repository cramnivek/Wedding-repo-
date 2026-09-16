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

Typefaces, all four self-hosted from `fonts/`: **Diablo Heavy** for the names
(see the note in there — it is a 1997 fan face, not the games' own Exocet),
**Cinzel** for every heading and letterspaced cap, **Cormorant Garamond** for
body text, **Allura** for the footer monogram. The last three came from Google
Fonts and are served from here rather than fetched from it — see *Putting it on
a domain* for why.

The display face is used for the names and nothing else. It has no true
lowercase — lowercase input selects alternate capital forms, which is what puts
the slashed `O` in FLORENCE — so it cannot set a heading, a label or a line of
body text. If any font fails to load the page falls back to system serif and
still reads correctly.

The eclipse, its corona, the light falling from it, the fog, the dead branches,
the ash and the whole opening gate are all drawn on `<canvas>` at runtime.

The ash is the one thing on that canvas with real depth. Everything else fakes
it by layering — each layer assigned a parallax rate and slid at it — but every
fleck of ash has an actual z, and its size, its speed across the screen as you
scroll, and how much of the dark has eaten its colour all fall out of one
perspective divide. What sells it is the tumble: each fleck is a flat scrap with
its own two rates of turn, and the second foreshortens it, so a scrap goes
edge-on and opens out again. Layered sprites never do that. No library and no
WebGL — four points, a multiply and a divide, per fleck, per frame, and
`check/fps.cjs` measures it at **0.5 fps** of a 14 fps budget.

The **distant fires** are there for a measured reason. All fifteen plates sit in
the first half of the page, and sampling the painted result section by section
showed what that cost: the grounds are identical throughout, rgb(19,16,14) give
or take a level, but the brightest 5% of a section with a plate reaches 60–130
and of one without reaches 22. The order of the day, travel, the RSVP and the
questions had no tonal range at all — legible and dead.

So they get a light instead of a picture: a wide, low ember glow anchored near
the foot of each, as though something were burning off the bottom of the frame,
one per screenful so a long section passes through light more than once. The
flattest screenful went from **22.7 to 34.0** with the image-rich sections
untouched, and body-text contrast held at 8.8–9.2:1 against the lifted ground,
well clear of the 4.5 floor. They cost nothing measurable in frame time.

They are anchored in document space and re-measured whenever the height changes,
which is not optional: `size()` runs before the lazy plates have loaded, and
anchoring once left the last four screenfuls exactly as dead as they started.

That budget is the thing to watch, not the ash. `check/fps.cjs` runs the page at
390px under 4× CPU throttling, roughly a mid-range Android, and it found the
fog costing two and a half times everything else on the canvas put together:
seven near-fullscreen additive composites every frame. It now draws into a
half-resolution buffer and blits up — 9.7 to 14.9 fps — because the cost was
fill rate, not the gradients. Pre-rendering those alone had only bought 1.8.

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
  by codec. mp4 266/474/333/321 KB, webm 313/665/401/423 KB. See below.
- **`rescue.mp4` / `rescue.webm`** — a fifth clip, ~360 KB each, **not served
  by the page**: its likenesses didn't survive being animated. Kept because the
  machinery to play it is still there and one attribute switches it on.
- The two favicons and `icon-512.png`.

None of the video is in the cold load — each clip is fetched only on scrolling
near its plate. `check/weigh.cjs` measures the desktop cold load and
`check/phone.cjs` measures what a phone actually pays, which is the number that
matters here; see *What it costs on a phone* below. If either climbs a long way,
something went in at full size.

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
the ink runs, and the envelope tears — and goes with the tear, fading out across
it rather than staying drawn around the opening, which would leave the eruption
playing inside a rectangle. What is left is the tear, and it opens into the
eclipse.

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
pays for it.

**They loop.** `clip.py --loop` dissolves each clip's tail over its own head
before encoding, which is what makes that possible: measured across the four,
the last frame and the first of the raw clips differ by a mean of 9 to 26 levels
and a worst-1% of 78 to 194, all of which snap visibly on every wrap. After the
dissolve every wrap is *within the frame-to-frame motion the clip has anyway* —
2.4 against 2.3 on `vow`, 6.1 against 5.3 on `camp` — so the join is no more
visible than an ordinary frame advance. `camp` looks like the worst of them on
paper and is not: its numbers are high at both ends because firelight moves that
much every single frame.

The cost is one second of length. Each is 9 seconds rather than 10.

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
python3 clip.py chamber art-source/chamber-clip.mp4 --crop 720:720:230:0 --loop
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
| Before the seal is broken | **1.03 MB** over 20 requests |
| Gate opened, before any scrolling | **2.21 MB** over 21 requests |
| After scrolling the whole page | **4.51 MB** over 35 requests |
| …of which video | **1.8 MB** (1.4 MB on Safari, which takes the mp4) |
| …of which music | **1.18 MB**, all of it at the press |
| …of which fonts | **214 KB** across 7 faces |

Measured against the live site, not a local build. The jump at the press is the
music: on a fast connection the browser pulls the whole track at once, and on
real mobile data it streams, so 1.18 MB is the ceiling rather than the typical
case. It is still the single largest thing here and the first place to look if
this number has to come down — 64k stereo would roughly halve it.

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

## The music bed

`audio/theme.m4a` and `audio/theme.ogg` — *Shaman Village* from the Shadow of
the Erdtree score, the same music the page's palette was built to sit with.
1.49 MB and 1.20 MB; only one is fetched, and only once the seal is broken.
`art-source/theme-source.mp3` is what it was made from.

To replace it, put another audio file through `music.py`:

```sh
python3 music.py theme.mp3
```

It writes both encodings; the page fetches whichever one the browser says it can
decode and nothing else needs changing. If `audio/` is empty the page asks, gets
a 404 and carries on silent — the bed is optional, not required. What the
script does that matters: normalises to **-18 LUFS**, which is quiet, because
this plays under a page nobody opened for the music and a track at its mastered
level arrives like a shout; trims silence off both ends, because a second of
room tone is a second of nothing every time it loops; and fades 0.6s at each end
so the wrap is a dip rather than a click. Audio is less forgiving than video
here — a discontinuity in a waveform is an audible pop, not a soft cut. Mono
unless you pass `--stereo`.

**It cannot start on its own.** No browser plays audible sound without a real
gesture, and there is exactly one on this page worth using: the press that
breaks the seal. So the bed starts there, held back two seconds and faded up
over four, so what you hear first is the blow and what you are left with is the
music. Nothing is fetched until that press — a guest who never opens the gate,
or has the sound off, pays nothing for it — and it streams, so it starts long
before it has all arrived.

The existing Sound toggle controls it, and remembers. Turning the sound on
*after* the gate has opened starts the music then, because that click is itself
a valid gesture; turning it on beforehand does not start anything early.

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

There are two flows in the Cloudflare dashboard and they need different things.

**Workers Builds** (build command plus a `npx wrangler deploy` deploy command)
is what `wrangler.jsonc` here is for. It has no Worker script — the whole config
is the assets directory, because this is a static site. Set:

- build command: `sh build.sh`
- deploy command: `npx wrangler deploy`
- root directory: `/`

**Classic Pages** wants no deploy command at all. If you use that instead,
delete `wrangler.jsonc` and set build command `sh build.sh`, output directory
`dist`.

Either way:

1. Deploy once and open the `*.workers.dev` or `*.pages.dev` URL it gives you.
   Check it there before pointing the domain at it.
2. **Add `marcandflo.com` as a custom domain** in the project's settings.
   Cloudflare adds the DNS record itself and issues the certificate, because the
   domain is registered in the same account. Add `www` if you want both to work.
3. **Paste the link into a message to yourself** and confirm the preview shows
   the eclipse and your names rather than a bare URL.

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
