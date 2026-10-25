const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const SRC = 'file:///home/user/claudecode/Offre_Decouverte_Fetes.html';
const OUT = '/home/user/claudecode';
const NAMES = ['01-accroche','02-notre-format','03-pour-les-fetes','04-pour-votre-activite','05-sur-votre-compte','06-qui-nous-sommes','07-nos-services','08-nos-realisations','09-l-offre-en-resume'];
(async () => {
  const b = await chromium.launch();
  // ---------- PDF ----------
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto(SRC); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  await p.pdf({ path: OUT + '/Offre_Decouverte_Fetes.pdf', width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  await p.close();

  // ---------- Carrousels Instagram : 1080 x 1350 ----------
  const q = await b.newPage({ viewport: { width: 432, height: 540 }, deviceScaleFactor: 2.5 });
  await q.goto(SRC); await q.evaluate(() => document.fonts.ready); await q.waitForTimeout(400);
  await q.addStyleTag({ content: `
    body>section.page:not(.ig){display:none}
    section.ig{width:432px;height:540px;padding:16px;box-sizing:border-box;overflow:hidden;background:#fff;scroll-snap-align:none}
    .ig .in{height:100%;padding:0;display:flex}
    .ig .trio{display:flex;flex:1;min-height:0}
    .ig .card{flex:1;height:100%;min-height:0}
    .ig .vis{flex:1 1 auto;height:auto;aspect-ratio:auto;min-height:0}
    .ig .row{padding:0;flex:1;align-content:center}
    .ig .row .t{font-size:5.2vw}
    .ig .row .d{font-size:3.7vw;line-height:1.35}
    .ig .row{row-gap:1vw}
    .ig .side-ph{flex:1 1 auto;aspect-ratio:auto;min-height:0}
  `});
  const plan = await q.evaluate(() => [...document.querySelectorAll('body>section.page')].map(s => s.querySelectorAll(':scope>.in>.card, :scope>.in>.trio>.card').length));
  console.log('cartes par diapo', plan);
  for (let i = 0; i < plan.length; i++) {
    const dir = path.join(OUT, 'Instagram_Offre_Decouverte', NAMES[i]);
    fs.mkdirSync(dir, { recursive: true });
    for (let j = 0; j < plan[i]; j++) {
      const info = await q.evaluate(([i, j]) => {
        document.querySelectorAll('section.ig').forEach(n => n.remove());
        const sec = document.querySelectorAll('body>section.page')[i];
        const card = sec.querySelectorAll(':scope>.in>.card, :scope>.in>.trio>.card')[j];
        const ns = sec.cloneNode(false); ns.classList.add('ig');
        const nin = sec.querySelector(':scope>.in').cloneNode(false); ns.appendChild(nin);
        let host = nin;
        if (card.parentElement.classList.contains('trio')) { host = card.parentElement.cloneNode(false); nin.appendChild(host); }
        const c = card.cloneNode(true); host.appendChild(c);
        // pas de prix sur Instagram
        const sub = c.querySelector('.cover-sub');
        if (sub) sub.innerHTML = '10&nbsp;vidéos tournées chez vous en 2&nbsp;heures.';
        c.querySelectorAll('.price').forEach(n => n.remove());
        document.body.prepend(ns);
        const r = c.getBoundingClientRect();
        // contenu qui dépasse de la carte (hors téléphone de couverture, coupé exprès)
        const over = [...c.querySelectorAll('p,h1,h2,span,.stack,.row,.vis,figure')].filter(n => !n.closest('.cover-tel')).some(n => { const b = n.getBoundingClientRect(); return b.bottom > r.bottom + 1 || b.right > r.right + 1; });
        return { over, txt: c.innerText.includes('€') };
      }, [i, j]);
      await q.waitForTimeout(150);
      const file = path.join(dir, String(j + 1).padStart(2, '0') + '.png');
      await q.locator('section.ig').screenshot({ path: file });
      console.log(file.replace(OUT + '/', ''), info.over ? 'DÉPASSE' : 'ok', info.txt ? 'PRIX!' : '');
    }
  }
  await b.close();
})();
