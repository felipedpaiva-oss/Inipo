// Renderiza o HTML em PDF (A3 paisagem) e gera PNGs de conferência.
// Uso: node render_pdf.js [dir_png]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const dir = __dirname;
  const pngDir = process.argv[2] || dir;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1587, height: 1123 } });
  await page.goto('file://' + path.join(dir, 'processo-atendimento-ia.html'));
  await page.pdf({ path: path.join(dir, 'processo-atendimento-ia.pdf'), format: 'A3', landscape: true, printBackground: true });
  await page.emulateMedia({ media: 'print' });
  const sections = await page.$$('section.page');
  for (let i = 0; i < sections.length; i++) {
    await sections[i].screenshot({ path: path.join(pngDir, `pagina${i + 1}.png`) });
  }
  await browser.close();
  console.log('ok');
})();
