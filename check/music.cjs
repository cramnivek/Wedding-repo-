/* The music bed: that it costs nothing until it is wanted, and that the page
 * is fine without it.
 *
 * Runs against whatever is in audio/ — including nothing. The bed is optional
 * by design, so "no file present" is a case to prove rather than a gap. */
const { chromium } = require('playwright-core');
const PAGE = 'file://' + __dirname + '/../index.html';

async function run(label, soundOn) {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const p = await b.newPage({ viewport: { width: 900, height: 900 } });

  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  const asked = [];
  p.on('request', r => { if (/\.(m4a|ogg|mp3)$/.test(r.url())) asked.push(r.url().split('/').pop()); });

  // The toggle remembers its setting, so set it before the page reads it.
  await p.addInitScript(v => {
    try { localStorage.setItem('mkf-sound', v); } catch (e) {}
  }, soundOn ? 'on' : 'off');

  await p.goto(PAGE);
  await p.waitForTimeout(2800);
  const beforePress = asked.length;

  await p.click('#gate-btn');
  await p.waitForTimeout(9000);

  const s = await p.evaluate(() => {
    const a = document.querySelector('audio');
    if (!a) return { exists: false };
    return {
      exists: true,
      loop: a.loop,
      preload: a.preload,
      // volume is the thing that throws if a fade steps outside 0..1
      volume: Math.round(a.volume * 1000) / 1000,
      types: [].map.call(a.children, s => s.type)
    };
  });

  console.log(label +
    ' — fetched before the press: ' + beforePress +
    ' | after: ' + asked.length + ' ' + JSON.stringify(asked) +
    '\n    element: ' + JSON.stringify(s) +
    '\n    errors: ' + JSON.stringify(errs));

  await b.close();
}

(async () => {
  await run('sound on ', true);
  await run('sound off', false);
})();
