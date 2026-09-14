const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  // The wedding is 17:00 in Bohol = 09:00 UTC. Every viewer must agree on that.
  for (const tz of ['Asia/Manila', 'Europe/London', 'America/Los_Angeles', 'UTC']) {
    const ctx = await b.newContext({ timezoneId: tz, viewport: { width: 900, height: 800 } });
    const p = await ctx.newPage();
    await p.goto('file://' + __dirname + '/../index.html');
    await p.evaluate(() => { const g=document.getElementById('gate'); if(g) g.remove(); document.body.classList.remove('gated'); });
    await p.waitForTimeout(900);
    const r = await p.evaluate(() => {
      const href = document.getElementById('cal').getAttribute('href');
      const dates = decodeURIComponent((href.match(/dates=([^&]+)/) || [])[1] || '');
      const el = document.getElementById('countdown');
      return { dates, countdown: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 34) };
    });
    console.log(tz.padEnd(20), r.dates, '|', r.countdown);
    await ctx.close();
  }
  await b.close();
})();
