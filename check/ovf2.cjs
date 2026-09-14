const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  for (const vw of [390, 430, 768, 1000, 1440]) {
    const p = await b.newPage({ viewport: { width: vw, height: 820 } });
    await p.goto('file://' + __dirname + '/../index.html');
    await p.evaluate(() => { const g = document.getElementById('gate'); if (g) g.remove(); document.body.classList.remove('gated'); });
    await p.waitForTimeout(1100);
    const r = await p.evaluate(() => {
      const f = document.querySelector('.band-img').getBoundingClientRect();
      return { over: document.documentElement.scrollWidth - document.documentElement.clientWidth,
               band: Math.round(f.left) + '..' + Math.round(f.right), vp: document.documentElement.clientWidth };
    });
    console.log(vw, JSON.stringify(r));
    await p.close();
  }
  await b.close();
})();
