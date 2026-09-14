const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const errs = [];

  // 1. Normal motion: gate completes, page unlocks, countdown ticks.
  const p = await b.newPage({ viewport: { width: 900, height: 900 } });
  p.on('pageerror', e => errs.push('normal: ' + e));
  await p.goto('file://' + __dirname + '/../index.html');
  await p.waitForTimeout(3000);
  await p.click('#gate-btn');
  await p.waitForTimeout(6200);
  console.log('gate gone:', !(await p.$('#gate')),
              '| scroll unlocked:', !(await p.evaluate(() => document.body.classList.contains('gated'))),
              '| countdown:', (await p.textContent('#countdown')).replace(/\s+/g,' ').trim().slice(0,52));
  const mailto = await p.getAttribute('footer a[href^="mailto:"]', 'href');
  console.log('footer mailto:', mailto);

  // 2. Reduced motion: gate must be removed outright, page usable immediately.
  const p2 = await b.newPage({ viewport: { width: 900, height: 900 } });
  await p2.emulateMedia({ reducedMotion: 'reduce' });
  p2.on('pageerror', e => errs.push('reduced: ' + e));
  await p2.goto('file://' + __dirname + '/../index.html');
  await p2.waitForTimeout(900);
  console.log('reduced — gate gone:', !(await p2.$('#gate')),
              '| unlocked:', !(await p2.evaluate(() => document.body.classList.contains('gated'))));

  // 3. Phone width: gate fits, no horizontal scroll on the page.
  const p3 = await b.newPage({ viewport: { width: 390, height: 780 } });
  p3.on('pageerror', e => errs.push('phone: ' + e));
  await p3.goto('file://' + __dirname + '/../index.html');
  await p3.waitForTimeout(2600);
  await p3.screenshot({ path: '/tmp/phone-gate.png' });
  await p3.click('#gate-btn');
  await p3.waitForTimeout(6200);
  const over = await p3.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log('phone — gate gone:', !(await p3.$('#gate')), '| horizontal overflow px:', over);

  console.log('errors:', errs);
  await b.close();
})();
