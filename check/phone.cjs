/* What a phone actually does with the clips.
 *
 * Desktop Chromium is the easy case. Autoplay-muted-inline is where mobile
 * browsers differ, and the deferred payload lands on whoever is opening this on
 * mobile data — which is most of the people it is being sent to. So this walks
 * the page at phone width with isMobile on, and reports what played and what it
 * cost to get there.
 *
 * isMobile also stops Playwright forcing a layout width, which is the only way
 * a missing viewport meta shows up (see vp.cjs). */
const { chromium } = require('playwright-core');
const PAGE = 'file://' + __dirname + '/../index.html';

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const ctx = await b.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 '
             + '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
  });
  const p = await ctx.newPage();

  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));

  // Count what crosses the wire, split into what arrives before anyone scrolls
  // and what the clips add on the way down.
  let bytes = 0, videoBytes = 0, reqs = 0;
  const fetched = [];
  p.on('response', async r => {
    reqs++;
    let n = 0;
    try { n = (await r.body()).length; } catch (e) { n = 0; }
    bytes += n;
    if (/\.(mp4|webm)$/.test(r.url())) { videoBytes += n; fetched.push(r.url().split('/').pop()); }
  });

  await p.goto(PAGE);
  await p.waitForTimeout(2600);
  await p.tap('#gate-btn');
  await p.waitForTimeout(6200);

  const cold = bytes, coldReqs = reqs;

  // Scroll the whole page the way a reader would, in screen-ish steps.
  await p.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 600) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 260));
    }
  });
  await p.waitForTimeout(5000);

  const clips = await p.evaluate(() =>
    [].map.call(document.querySelectorAll('[data-clip]'), f => {
      const v = f.querySelector('video');
      return {
        name: f.getAttribute('data-clip').replace('img/', ''),
        swapped: !!v,
        advanced: v ? +(v.currentTime.toFixed(1)) : null,
        inline: v ? v.playsInline : null
      };
    }));

  const over = await p.evaluate(() =>
    document.documentElement.scrollWidth - document.documentElement.clientWidth);
  const layout = await p.evaluate(() => document.documentElement.clientWidth);

  const KB = n => Math.round(n / 1024);
  console.log('layout width:', layout, '| horizontal overflow:', over);
  console.log('cold (gate opened, no scroll):', KB(cold), 'KB over', coldReqs, 'requests');
  console.log('after scrolling the whole page:', KB(bytes), 'KB over', reqs, 'requests');
  console.log('of which video:', KB(videoBytes), 'KB', JSON.stringify(fetched));
  clips.forEach(c => console.log('   ', c.name,
    '— swapped:', c.swapped, '| played to:', c.advanced + 's', '| playsInline:', c.inline));
  console.log('errors:', errs);

  /* Data Saver: the page should fetch no video at all. navigator.connection is
     read-only and not settable from page script, so it is stubbed on the window
     before any of the page's own script runs. */
  const ctx2 = await b.newContext({
    viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true
  });
  const p2 = await ctx2.newPage();
  await p2.addInitScript(() => {
    Object.defineProperty(navigator, 'connection', {
      configurable: true,
      value: { saveData: true, effectiveType: '4g' }
    });
  });
  let saverVideo = 0;
  p2.on('request', r => { if (/\.(mp4|webm)$/.test(r.url())) saverVideo++; });
  await p2.goto(PAGE);
  await p2.waitForTimeout(2600);
  await p2.tap('#gate-btn');
  await p2.waitForTimeout(6200);
  await p2.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 600) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 200));
    }
  });
  await p2.waitForTimeout(3000);
  // Counted from the page rather than written down here, so adding a clip does
  // not quietly turn this line into a lie about how many were checked.
  const [stillsLeft, clipCount] = await p2.evaluate(() => [
    document.querySelectorAll('[data-clip] picture').length,
    document.querySelectorAll('[data-clip]').length]);
  console.log('data saver — video files fetched:', saverVideo,
              '| stills left in place:', stillsLeft, 'of', clipCount);

  await b.close();
})();
