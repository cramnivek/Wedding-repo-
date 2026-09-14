const { chromium } = require('playwright-core');
const lum = ([r,g,b]) => { const f=c=>{c/=255; return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4);};
  return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b); };
const ratio = (a,b) => { const [x,y]=[lum(a),lum(b)].sort((m,n)=>n-m); return (x+0.05)/(y+0.05); };
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
  for (const [label, file] of [['AFTER (beam+sky)', __dirname + '/../index.html'],
                               ['BEFORE (committed)', __dirname + '/../index.html']]) {
    const p = await b.newPage({ viewport: { width: 1000, height: 900 } });
    await p.goto('file://' + file);
    await p.evaluate(() => { const g=document.getElementById('gate'); if(g) g.remove(); document.body.classList.remove('gated'); });
    await p.waitForTimeout(3600);
    const out = await p.evaluate(() => {
      const c = document.getElementById('art'), g = c.getContext('2d');
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const grab = (x,y) => Array.from(g.getImageData(Math.round(x*dpr), Math.round(y*dpr), 1, 1).data).slice(0,3);
      const res = [];
      document.querySelectorAll('#countdown .l').forEach(el => {
        const r = el.getBoundingClientRect();
        res.push({ t: el.textContent, bg: grab(r.left + r.width/2, r.top + r.height/2) });
      });
      const n = document.querySelector('#countdown .n');
      const nr = n.getBoundingClientRect();
      return { labels: res, numeral: grab(nr.left + nr.width/2, nr.top + nr.height*0.8) };
    });
    console.log('--- ' + label);
    out.labels.forEach(o => console.log('  label "' + o.t + '" bg=' + o.bg.join(',') +
      '  --bone-soft ' + ratio([196,178,150], o.bg).toFixed(2) + ':1'));
    console.log('  numeral bg=' + out.numeral.join(',') + '  --bone ' + ratio([235,220,192], out.numeral).toFixed(2) + ':1');
    await p.close();
  }
  await b.close();
})();
