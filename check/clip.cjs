/* The rescue clip swaps in for the still, and only when it should.
 *
 * Four things worth proving: that nothing is fetched while the gate is still
 * up, that nothing is fetched until the section is near, that the video
 * actually replaces the picture once it has decoded a frame, and that someone
 * who asked for reduced motion is left with the still and no download at all.
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
  const afterGate = asked.length;

  await p.evaluate(() => document.getElementById('us').scrollIntoView());
  await p.waitForTimeout(3000);

  const s = await p.evaluate(() => {
    /* The clip is switched on and off by the presence of data-clip on the
       figure. Find the plate either way, so that with the clip off this
       reports "off, still intact" rather than a row of nulls that reads as
       a pass. */
    const fig = document.querySelector('.plate-ink');
    const on = !!(fig && fig.hasAttribute('data-clip'));
    const v = fig && fig.querySelector('video');
    return {
      on: on,
      video: !!v,
      still: !!(fig && fig.querySelector('picture')),
      playing: v ? (!v.paused && v.currentTime > 0) : null,
      muted: v ? v.muted : null,
      labelled: v ? !!v.getAttribute('aria-label') : null,
      loops: v ? v.loop : null
    };
  });

  if (!s.on) {
    console.log((reduced ? 'reduced' : 'normal ') +
      ' — clip OFF (no data-clip) | still in figure: ' + s.still +
      ' | video files fetched: ' + asked.length);
    await b.close();
    return;
  }

  console.log(
    (reduced ? 'reduced' : 'normal ') +
    ' — fetched during gate: ' + duringGate +
    ' | after gate, before scroll: ' + afterGate +
    ' | total: ' + asked.length + ' ' + JSON.stringify(asked) +
    ' | video: ' + s.video + ' | still left: ' + s.still +
    ' | playing: ' + s.playing + ' | muted: ' + s.muted +
    ' | labelled: ' + s.labelled + ' | loops: ' + s.loops);

  await b.close();
}

(async () => { await run(false); await run(true); })();
