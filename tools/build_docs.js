// Renders docs/src/*.html to docs/pdf/*.pdf (A4). Usage: node tools/build_docs.js
// Uses the Playwright + Chromium already installed in the environment.
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..'), src = path.join(root, 'docs', 'src'), out = path.join(root, 'docs', 'pdf');
const map = { 'scheda_stampa_IT.html': 'scheda_stampa_KobraX_IT.pdf', 'print_sheet_EN.html': 'print_sheet_KobraX_EN.pdf',
              'istruzioni_montaggio_IT.html': 'istruzioni_montaggio_IT.pdf', 'assembly_instructions_EN.html': 'assembly_instructions_EN.pdf' };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [h, pdf] of Object.entries(map)) {
    if (!fs.existsSync(path.join(src, h))) continue;
    await p.goto('file://' + path.join(src, h));
    await p.pdf({ path: path.join(out, pdf), format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log(pdf);
  }
  await b.close();
})();
