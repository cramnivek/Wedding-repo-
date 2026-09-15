/* What the artwork canvas costs, on a phone that is not fast.
 *
 * 4x CPU throttling against a desktop core is roughly a mid-range Android. A
 * current iPhone is much better than this; the number is here to be compared
 * against itself after a change, not to be read as what any particular guest
 * sees.
 *
 * Pass a layer name to measure the page without it — that is how drawFog was
 * found to be two and a half times the cost of everything else put together:
 *
 *   node fps.cjs                 the page as it stands
 *   node fps.cjs drawFog         the same page with that layer removed
 */
const { chromium } = require('playwright-core');
const fs = require('fs');
const os = require('os');
const path = require('path');

const LAYERS = ['drawRays', 'drawEclipse', 'drawFog', 'drawBranches', 'drawMotes', 'drawEmbers'];

async function measure(htmlPath) {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const ctx = await b.newContext({
    viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true
  });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  await p.goto('file://' + htmlPath);
  await p.waitForTimeout(2800);
  await p.tap('#gate-btn').catch(() => {});
  await p.waitForTimeout(6500);

  const v = await p.evaluate(() => new Promise(res => {
    let n = 0; const t0 = performance.now();
    (function c() {
      n++;
      if (performance.now() - t0 < 3500) requestAnimationFrame(c);
      else res(n / ((performance.now() - t0) / 1000));
    })();
  }));

  await b.close();
  return { fps: v, errs };
}

(async () => {
  const src = path.resolve(__dirname, '..', 'index.html');
  const want = process.argv[2];

  if (!want) {
    const r = await measure(src);
    console.log('as it stands: ' + r.fps.toFixed(1) + ' fps  (4x throttle, 390px)');
    if (r.errs.length) console.log('errors:', r.errs);
    return;
  }

  if (LAYERS.indexOf(want) < 0) {
    console.log('unknown layer. one of: ' + LAYERS.join(', '));
    process.exit(1);
  }

  // Write the stripped copy beside the original so its relative asset paths
  // still resolve, and take it away again afterwards.
  const stripped = path.resolve(__dirname, '..', '.fps-probe.html');
  let s = fs.readFileSync(src, 'utf8');
  const before = s.length;
  s = s.replace(new RegExp('\\n *' + want + '\\(scroll\\);'), '')
       .replace(new RegExp('\\n *if \\(!still\\) ' + want + '\\(\\);'), '');
  if (s.length === before) {
    console.log('found no call to ' + want + ' in scene()');
    process.exit(1);
  }
  fs.writeFileSync(stripped, s);
  try {
    const base = await measure(src);
    const cut = await measure(stripped);
    console.log('with ' + want + ':    ' + base.fps.toFixed(1) + ' fps');
    console.log('without ' + want + ': ' + cut.fps.toFixed(1) + ' fps   (+' +
                (cut.fps - base.fps).toFixed(1) + ')');
  } finally {
    fs.unlinkSync(stripped);
  }
})();
