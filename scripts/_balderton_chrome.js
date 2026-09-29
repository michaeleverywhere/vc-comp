const fs = require('fs');
const path = require('path');
const puppeteer = require(process.env.PUPPETEER_PATH || path.join('/tmp/vc-recon/node_modules/puppeteer-core'));
(async () => {
  const outPath = process.argv[2];
  if (!outPath) { console.error('usage: node _balderton_chrome.js <out.json>'); process.exit(1); }
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
    headless: 'new',
    args: ['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']
  });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36');
  await page.goto('https://www.balderton.com/companies/', {waitUntil: 'networkidle2', timeout: 90000});
  const totalPages = await page.evaluate(() => (FWP.settings.pager && FWP.settings.pager.total_pages) || 9);
  const totalRows = await page.evaluate(() => (FWP.settings.pager && FWP.settings.pager.total_rows) || 0);
  async function scrapeCards() {
    return page.evaluate(() => [...document.querySelectorAll('.company.type-company')].map(c => {
      const name = (c.querySelector('h3') || {}).innerText || '';
      const location = (c.querySelector('span.label-M') || {}).innerText || '';
      const desc = (c.querySelector('.body-s') || {}).innerText || '';
      const stage = (c.querySelector('ul.list-inline') || {}).innerText || '';
      const a = c.querySelector('a.mask[href], a[href^="http"]');
      const url = a ? a.href : '';
      const logo = (c.querySelector('img.logo') || {}).src || '';
      const classes = [...c.classList];
      return {name: name.trim(), location: location.trim(), description: desc.trim(),
              stage: stage.trim(), company_url: url, logo_url: logo, classes};
    }));
  }
  let all = await scrapeCards();
  for (let p = 2; p <= totalPages + 1; p++) {
    const before = await page.$$eval('.company.type-company', els => els.length);
    await page.evaluate((pageNum) => { FWP.is_load_more = true; FWP.paged = pageNum; FWP.refresh(); }, p);
    try {
      await page.waitForFunction(
        (prev) => document.querySelectorAll('.company.type-company').length > prev,
        {timeout: 20000}, before
      );
    } catch (e) { break; }
    all = await scrapeCards();
    const seen = new Set(); let n = 0;
    for (const c of all) { if (c.name && !seen.has(c.name)) { seen.add(c.name); n++; } }
    process.stderr.write(`page ${p} unique=${n}\n`);
    if (n >= totalRows) break;
  }
  const seen = new Set(); const uniq = [];
  for (const c of all) {
    if (!c.name || seen.has(c.name)) continue;
    seen.add(c.name); uniq.push(c);
  }
  fs.writeFileSync(outPath, JSON.stringify(uniq));
  process.stderr.write(`wrote ${uniq.length} -> ${outPath}\n`);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
