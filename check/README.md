# check

Browser checks for `../index.html`. Every one of these exists because it caught
something real.

```sh
cd check
npm install
npx playwright install chromium     # or set CHROME_PATH to a Chromium you have
npm run all
```

`CHROME_PATH` overrides the browser if you already have one on disk.

| Script | What it caught |
| --- | --- |
| `vp.cjs` | The page had **no viewport meta**. A phone laid it out at 980px and zoomed out. Invisible in a plain headless viewport — needs `isMobile: true` to reproduce. |
| `tz.cjs` | The date had no timezone, so it was parsed in the **visitor's** zone. A guest abroad got a countdown and a calendar entry hours out. Checks Manila, London, Los Angeles and UTC agree. |
| `ovf2.cjs` | Horizontal scroll at five widths. Found the header scrim overflowing 156px, which `overflow-x: hidden` was hiding but not preventing. |
| `final.cjs` | Gate completes, scroll unlocks, reduced-motion removes the gate outright, no JS errors. |
| `snd.cjs` | Sound builds one audio context and four oscillators when on, **zero** when off, and defaults off under reduced motion. |
| `music.cjs` | The music bed: nothing fetched before the seal is broken, exactly **one** encoding after, none at all with the sound off, and no audio element built in that case either. Runs with or without a file in `audio/` — the bed is optional, so its absence is a case to prove, not a gap. Caught a fade setting `volume` to -0.0009 and throwing. |
| `contrast2.cjs` | Contrast measured against the **composited canvas pixel**, not the CSS token. Found the countdown labels at 4.3:1, under the AA floor. |
| `weigh.cjs` | Total delivered bytes and the ten largest files, over a local server so caching does not lie. |
| `clip.cjs` | Every `data-clip` plate: nothing fetched while the gate is up, nothing fetched until the plate is near, exactly **one** of the two encodings downloaded per clip, the video swapped in only after it decodes a frame, and reduced motion left with the stills and zero bytes. Caught `data-clip` producing `rescue.mp4.mp4`, and a bare `video/mp4` type causing **both** files to download. |
| `phone.cjs` | What a phone actually pays: cold bytes before scrolling, total after, and how much of it is video — at 390px with `isMobile`, which is the only setup that tells the truth. Also proves Data Saver gets **no** video and keeps all four stills. |
| `fps.cjs` | Frame rate of the artwork canvas at 390px under 4x CPU throttling — roughly a mid-range Android. Pass a layer name to measure the page without it. Found `drawFog` costing two and a half times everything else on the canvas put together: seven near-fullscreen additive composites per frame. |
| `maxsize.cjs` | Largest CSS width each image ever renders at, across seven viewports — what the files should actually be sized to. |
| `seam.cjs` `beh2.cjs` `live.cjs` | Frame captures of the gate and the page sections, on a frozen clock so a screenshot's own latency cannot advance the animation. |

`fonts/` holds the latin subsets of Cinzel and Cormorant Garamond. A sandboxed
headless Chromium generally cannot reach `fonts.gstatic.com`, so `live.cjs`
injects them as data URIs — without that the captures come back in system serif
and look like a font bug that isn't there.

## Two things that will mislead you

**A plain Playwright viewport forces the layout width**, which masks a missing
viewport meta entirely. `vp.cjs` uses `isMobile: true` for that reason.

**The frozen-clock captures pump rAF by hand.** If you change a timeline in
`index.html`, the frame marks in `seam.cjs` go stale and a working animation will
look broken. Check the arithmetic before believing the pictures.

**This Chromium has no H.264.** Playwright ships it without the proprietary
codecs, so it always picks the WebM and `clip.cjs` passing does not prove the
mp4 plays. Open the page in Safari for that.
