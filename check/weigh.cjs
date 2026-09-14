const { chromium } = require('playwright-core');
const http = require('http'); const fs = require('fs'); const path = require('path');
const MIME = {'.html':'text/html','.webp':'image/webp','.avif':'image/avif','.jpg':'image/jpeg','.png':'image/png','.woff2':'font/woff2'};
const srv = http.createServer((req,res)=>{
  let f = decodeURIComponent(req.url.split('?')[0]); if (f === '/') f = '/index.html';
  const p = path.join(__dirname, '..', f);
  if (!p.startsWith(path.join(__dirname, '..')) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
  fs.createReadStream(p).pipe(res);
});
srv.listen(0, async () => {
  const port = srv.address().port;
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  const p = await b.newPage({ viewport: { width: 1000, height: 900 } });
  const seen = new Map();
  p.on('response', async r => {
    try { const buf = await r.body(); seen.set(r.url(), buf.length); } catch (e) {}
  });
  await p.goto('http://localhost:' + port + '/index.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => { const g = document.getElementById('gate'); if (g) g.remove(); document.body.classList.remove('gated'); });
  // Scroll the whole page so lazy images actually load.
  await p.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); }
  });
  await p.waitForTimeout(1500);
  let total = 0; const rows = [];
  for (const [u, n] of seen) { total += n; rows.push([u.split('/').pop().split('?')[0], n]); }
  rows.sort((a,b) => b[1]-a[1]);
  console.log('requests:', seen.size, '| total', (total/1024/1024).toFixed(2), 'MB');
  rows.slice(0, 10).forEach(([n, s]) => console.log('  ', String(Math.round(s/1024)).padStart(5), 'KB  ', n));
  await b.close(); srv.close();
});
