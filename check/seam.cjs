const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const p = await b.newPage({ viewport: { width: 900, height: 860 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + __dirname + '/../index.html');
  await p.waitForTimeout(3000);
  await p.evaluate(() => {
    window.__fake = 0; window.__cbs = [];
    window.requestAnimationFrame = cb => { window.__cbs.push(cb); return 1; };
    window.__run = to => { while (window.__fake < to) { window.__fake += 16;
      const c = window.__cbs; window.__cbs = []; c.forEach(f => f(window.__fake)); } };
  });
  await p.click('#gate-btn');
  // The erupt phase runs from 2200 to 3700.
  for (const ms of [2760, 2900, 3080, 3320, 3620, 3950, 4250]) {
    await p.evaluate(m => window.__run(m), ms);
    await p.screenshot({ path: '/tmp/e' + ms + '.png' });
  }
  // The page as it will appear the instant the gate is gone.
  await p.evaluate(() => { const g = document.getElementById('gate'); g.remove(); document.body.classList.remove('gated'); });
  await p.evaluate(() => { window.requestAnimationFrame = cb => setTimeout(() => cb(performance.now()), 16); });
  await p.waitForTimeout(2500);
  await p.screenshot({ path: '/tmp/e_page.png' });
  console.log('errors:', errs);
  await b.close();
})();
