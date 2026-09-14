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
| `contrast2.cjs` | Contrast measured against the **composited canvas pixel**, not the CSS token. Found the countdown labels at 4.3:1, under the AA floor. |
| `weigh.cjs` | Total delivered bytes and the ten largest files, over a local server so caching does not lie. |
| `clip.cjs` | The rescue clip: nothing fetched while the gate is up, nothing fetched until the section is near, exactly **one** of the two encodings downloaded, the video swapped in only after it decodes a frame, and reduced motion left with the still and zero bytes. Caught `data-clip` producing `rescue.mp4.mp4`, and a bare `video/mp4` type causing **both** files to download. |
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
