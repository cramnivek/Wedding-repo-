const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined,
    args: ['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport: { width: 900, height: 860 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + __dirname + '/../index.html');
  // Instrument the Web Audio graph so we can prove it actually builds.
  await p.evaluate(() => {
    window.__audio = { contexts: 0, oscs: 0, started: false };
    const AC = window.AudioContext;
    window.AudioContext = function () {
      const c = new AC();
      window.__audio.contexts++;
      const oc = c.createOscillator.bind(c);
      c.createOscillator = function () { window.__audio.oscs++; return oc(); };
      return c;
    };
  });
  await p.waitForTimeout(2800);
  const before = await p.evaluate(() => ({
    label: document.getElementById('sound-toggle').textContent.trim(),
    pressed: document.getElementById('sound-toggle').getAttribute('aria-pressed'),
    fn: typeof window.gateSound
  }));
  console.log('before press:', JSON.stringify(before));
  await p.click('#gate-btn');
  await p.waitForTimeout(600);
  console.log('after press: ', JSON.stringify(await p.evaluate(() => window.__audio)));

  // Toggling off must persist and must silence the next press.
  const p2 = await b.newPage({ viewport: { width: 900, height: 860 } });
  await p2.goto('file://' + __dirname + '/../index.html');
  await p2.evaluate(() => { window.__audio = { contexts: 0 };
    const AC = window.AudioContext;
    window.AudioContext = function () { window.__audio.contexts++; return new AC(); }; });
  await p2.waitForTimeout(2600);
  await p2.evaluate(() => document.getElementById('sound-toggle').click());
  const off = await p2.evaluate(() => ({
    label: document.getElementById('sound-toggle').textContent.trim(),
    pressed: document.getElementById('sound-toggle').getAttribute('aria-pressed'),
    stored: localStorage.getItem('mkf-sound')
  }));
  await p2.click('#gate-btn');
  await p2.waitForTimeout(500);
  console.log('after toggle off:', JSON.stringify(off), '| contexts created:', await p2.evaluate(() => window.__audio.contexts));

  // Reduced motion should default it to off with nothing stored.
  const p3 = await b.newPage({ viewport: { width: 900, height: 860 } });
  await p3.emulateMedia({ reducedMotion: 'reduce' });
  await p3.goto('file://' + __dirname + '/../index.html');
  await p3.waitForTimeout(900);
  console.log('reduced-motion default:', await p3.evaluate(() =>
    document.getElementById('sound-toggle').getAttribute('aria-pressed')));
  console.log('errors:', errs);
  await b.close();
})();
