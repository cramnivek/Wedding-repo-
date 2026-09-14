const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const max = {};
  for (const vw of [1600, 1440, 1024, 768, 600, 430, 390]) {
    const p = await b.newPage({ viewport: { width: vw, height: 900 } });
    await p.goto('file://' + __dirname + '/../index.html');
    await p.evaluate(() => { const g=document.getElementById('gate'); if(g) g.remove(); document.body.classList.remove('gated'); });
    await p.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 50)); }
    });
    await p.waitForTimeout(700);
    const rows = await p.evaluate(() => [...document.querySelectorAll('img')].map(i => ({
      name: i.currentSrc.split('/').pop().replace(/\.\w+$/, ''),
      w: Math.round(i.getBoundingClientRect().width) })));
    rows.forEach(r => { if (!max[r.name] || r.w > max[r.name]) max[r.name] = r.w; });
    await p.close();
  }
  console.log('name              maxCSS   need@2x');
  Object.entries(max).sort().forEach(([k,v]) => console.log(k.padEnd(16), String(v).padStart(5), String(v*2).padStart(8)));
  await b.close();
})();
