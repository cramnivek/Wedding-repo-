const { chromium } = require('playwright-core');
const fs = require('fs');
const d = f => 'data:font/woff2;base64,' + fs.readFileSync(__dirname + '/fonts/' + f + '.woff2').toString('base64');
// This container's headless Chromium cannot reach Google Fonts, so the cached
// latin subsets are injected to see what a real visitor will actually get.
const CSS = ['Cinzel:Cinzel', 'Cormorant Garamond:CormorantGaramond']
  .map(p => { const [fam, file] = p.split(':'); return `@font-face{font-family:'${fam}';src:url('${d(file)}') format('woff2');font-display:block}`; }).join('');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const p = await b.newPage({ viewport: { width: 1000, height: 1200 }, deviceScaleFactor: 2 });
  await p.goto('file://' + __dirname + '/../index.html');
  await p.addStyleTag({ content: CSS });
  await p.evaluate(() => { const g = document.getElementById('gate'); if (g) g.remove(); document.body.classList.remove('gated'); });
  await p.waitForTimeout(3400);
  await p.screenshot({ path: '/tmp/live-head.png' });
  for (const [id, f] of [['us','/tmp/live-us.png'], ['faq','/tmp/live-faq.png'], ['reception','/tmp/live-rec.png']]) {
    await p.evaluate(i => document.getElementById(i).scrollIntoView(), id);
    await p.waitForTimeout(1400);
    await p.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.style.opacity = 1));
    await p.waitForTimeout(300);
    await p.locator('#' + id).screenshot({ path: f });
  }
  await b.close();
})();
