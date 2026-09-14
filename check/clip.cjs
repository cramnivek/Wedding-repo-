/* Every plate that carries data-clip swaps its still for a video, and only
 * when it should.
 *
 * Four things worth proving per clip: that nothing is fetched while the gate is
 * still up, that nothing is fetched until the section is near, that the video
 * actually replaces the picture once it has decoded a frame, and that someone
 * who asked for reduced motion is left with the stills and no download at all.
 *
 * Note this browser: Playwright's Chromium ships WITHOUT the proprietary
 * codecs, so it cannot decode H.264 and will always choose the WebM. That is
 * the reason both are published — but it also means a pass here does not prove
 * the mp4 plays. For that, open the page in Safari. */
const { chromium } = require('playwright-core');
const PAGE = 'file://' + __dirname + '/../index.html';

async function run(reduced) {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const p = await b.newPage({ viewport: { width: 900, height: 900 } });
  await p.emulateMedia({ reducedMotion: reduced ? 'reduce' : 'no-preference' });

  const asked = [];
  p.on('request', r => {
    if (/\.(mp4|webm)$/.test(r.url())) asked.push(r.url().split('/').pop());
  });

  await p.goto(PAGE);
  await p.waitForTimeout(3000);
  const duringGate = asked.length;

  if (!reduced) {
    await p.click('#gate-btn');
    await p.waitForTimeout(6200);
  }

  const clips = await p.evaluate(() =>
    [].map.call(document.querySelectorAll('[data-clip]'), f => f.getAttribute('data-clip')));

  if (!clips.length) {
    console.log((reduced ? 'reduced' : 'normal ') +
      ' — no clips on the page (no data-clip anywhere) | video files fetched: ' + asked.length);
    await b.close();
    return;
  }

  /* Scroll the whole page rather than to one section, so every clip gets its
     chance to arm — and so a clip that arms too early shows up as a fetch that
     happened before its own section was anywhere near. */
  await p.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 400) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 120));
    }
  });
  await p.waitForTimeout(3000);

  const rows = await p.evaluate(() =>
    [].map.call(document.querySelectorAll('[data-clip]'), f => {
      const v = f.querySelector('video');
      return {
        base: f.getAttribute('data-clip'),
        video: !!v,
        still: !!f.querySelector('picture'),
        playing: v ? (!v.paused && v.currentTime > 0) : null,
        muted: v ? v.muted : null,
        labelled: v ? !!v.getAttribute('aria-label') : null,
        loops: v ? v.loop : null
      };
    }));

  console.log((reduced ? 'reduced' : 'normal ') +
    ' — clips: ' + clips.length +
    ' | fetched during gate: ' + duringGate +
    ' | fetched total: ' + asked.length + ' ' + JSON.stringify(asked));
  rows.forEach(r => console.log('    ' + r.base +
    ' — video: ' + r.video + ' | still left: ' + r.still +
    ' | playing: ' + r.playing + ' | muted: ' + r.muted +
    ' | labelled: ' + r.labelled + ' | loops: ' + r.loops));

  await b.close();
}

(async () => { await run(false); await run(true); })();
