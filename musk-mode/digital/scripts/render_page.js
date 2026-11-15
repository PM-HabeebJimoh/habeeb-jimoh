const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ userAgent: 'Mozilla/5.0 (price research)' });
  for (const u of process.argv.slice(2)) {
    try {
      await p.goto(u, { waitUntil: 'networkidle', timeout: 45000 });
      await p.waitForTimeout(2500);
      const t = (await p.innerText('body')).replace(/\s+/g, ' ');
      console.log('=== ' + u + '\n' + t.slice(0, 3500));
    } catch (e) { console.log('=== ' + u + ' ERROR ' + e.message.slice(0, 120)); }
  }
  await b.close();
})();
