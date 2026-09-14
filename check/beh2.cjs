const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const p = await b.newPage({ viewport: { width: 820, height: 820 }, deviceScaleFactor: 1.6 });
  const errs = [], failed = [];
  p.on('pageerror', e => errs.push(String(e)));
  p.on('requestfailed', r => failed.push(r.url().split('/').pop()));
  await p.goto('file://' + __dirname + '/../index.html');
  await p.waitForTimeout(3200);
  console.log('sprite loaded:', await p.evaluate(() => !!document.querySelector('canvas')));
  await p.screenshot({ path: '/tmp/g_idle.png' });
  await p.evaluate(() => {
    window.__fake = 0; window.__cbs = [];
    window.requestAnimationFrame = cb => { window.__cbs.push(cb); return 1; };
    window.__run = to => { while (window.__fake < to) { window.__fake += 16;
      const c = window.__cbs; window.__cbs = []; c.forEach(f => f(window.__fake)); } };
  });
  await p.click('#gate-btn');
  for (const ms of [300, 700, 1100, 1500, 1900, 2300, 2700]) {
    await p.evaluate(m => window.__run(m), ms);
    await p.screenshot({ path: '/tmp/g' + ms + '.png' });
  }
  console.log('failed requests:', failed, '| errors:', errs);
  await b.close();
})();
