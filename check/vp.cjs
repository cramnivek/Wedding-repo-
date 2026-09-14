const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  // isMobile makes Chromium honour (or miss) the viewport meta the way a phone does.
  const ctx = await b.newContext({ viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true,
    deviceScaleFactor: 3 });
  const p = await ctx.newPage();
  await p.goto('file://' + __dirname + '/../index.html');
  await p.waitForTimeout(1200);
  console.log(await p.evaluate(() => ({
    viewportMeta: document.querySelector('meta[name=viewport]') ? 'present' : 'MISSING',
    layoutWidth: document.documentElement.clientWidth,
    windowWidth: window.innerWidth
  })));
  await b.close();
})();
