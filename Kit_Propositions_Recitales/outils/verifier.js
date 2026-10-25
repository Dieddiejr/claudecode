/*
  verifier.js : contrôle une proposition construite et fait une capture de chaque diapo.

      node outils/verifier.js projets/MON-PROJET/proposition.html

  Produit, dans projets/MON-PROJET/controle/ :
    diapo-01.png, diapo-02.png ...  (chaque diapo en 1920 x 1080, à regarder une par une)
    telephone.png                   (la page entière sur un écran de téléphone de 390 px)
  Et affiche la liste des problèmes. Code de sortie 1 s'il y en a.

  Problèmes détectés :
    - DÉBORDE   : un texte ou une image sort de sa carte (texte trop long, trop de lignes)
    - IMAGE     : une image n'a pas pu être chargée
    - VIDE      : un emplacement de texte est vide
    - NOMBRE    : mauvais nombre de cartes ou de lignes pour le gabarit
    - POLICE    : la police Schibsted Grotesk n'est pas chargée
    - BOUTON    : le texte du bouton passe sur 2 lignes
    - ALIGNEMENT: dans G04, un texte trop long décale la photo de sa carte
    - TÉLÉPHONE : la page déborde sur la largeur d'un téléphone
*/
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const file = process.argv[2];
if (!file || !fs.existsSync(file)) { console.error('Usage : node outils/verifier.js chemin/vers/proposition.html'); process.exit(2); }
const abs = path.resolve(file);
const outDir = path.join(path.dirname(abs), 'controle');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + abs);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  const report = await page.evaluate(() => {
    const out = [];
    const textRight = n => { const g = document.createRange(); g.selectNodeContents(n); return g.getBoundingClientRect().right; };
    if (!document.fonts.check('500 20px "Schibsted Grotesk"')) out.push({ d: 0, type: 'POLICE', msg: 'Schibsted Grotesk non chargée : reconstruis avec construire.py' });
    const pages = [...document.querySelectorAll('body > section.page')];
    pages.forEach((sec, i) => {
      const d = i + 1;
      const txt = n => (n.innerText || n.getAttribute('alt') || n.className || '').replace(/\s+/g, ' ').trim().slice(0, 60);
      sec.querySelectorAll('.card').forEach(card => {
        const r = card.getBoundingClientRect();
        const box = sec.getBoundingClientRect();
        if (r.bottom > box.bottom + 1 || r.right > box.right + 1) {
          out.push({ d, type: 'DÉBORDE', msg: 'la carte « ' + txt(card).slice(0, 40) + ' » sort de la diapo : trop de texte' });
          return;
        }
        const tel = card.querySelector('.cover-tel'), st = card.querySelector('.stack');
        if (tel && st && st.getBoundingClientRect().bottom > tel.getBoundingClientRect().top - 10) {
          out.push({ d, type: 'DÉBORDE', msg: 'le texte de la couverture touche le téléphone : raccourcis G01_PROMESSE ou G01_DETAIL' });
        }
        const els = [...card.querySelectorAll('p,h1,h2,span.label,.stack,.row,.vis,.side-ph,.intro-ph,a.btn,figure')]
          .filter(n => !n.closest('.cover-tel') && !(n.closest('.fx') && n.tagName !== 'FIGURE'));
        for (const n of els) {
          const b = n.getBoundingClientRect();
          if (/^(P|H1|H2|SPAN)$/.test(n.tagName) && textRight(n) > r.right - parseFloat(getComputedStyle(card).paddingRight) / 2) {
            out.push({ d, type: 'DÉBORDE', msg: '« ' + txt(n) + ' » : un mot est trop long pour la largeur (il dépasse sur le côté)' });
            break;
          }
          if (b.bottom > r.bottom + 1 || b.right > r.right + 1) {
            out.push({ d, type: 'DÉBORDE', msg: '« ' + txt(n) + ' » sort de sa carte de ' + Math.round(Math.max(b.bottom - r.bottom, b.right - r.right)) + ' px' });
            break;
          }
        }
      });
      sec.querySelectorAll('img').forEach(im => { if (!im.complete || !im.naturalWidth) out.push({ d, type: 'IMAGE', msg: 'image non chargée (' + (im.alt || 'sans description') + ')' }); });
      sec.querySelectorAll('h1,h2,p.s,p.x,p.t,p.d,.cover-big,.cover-sub,span.label').forEach(n => { if (!n.textContent.trim()) out.push({ d, type: 'VIDE', msg: 'texte vide dans ' + n.tagName.toLowerCase() + '.' + n.className }); });
      sec.querySelectorAll('a.btn').forEach(bt => {
        const cs = getComputedStyle(bt), one = parseFloat(cs.fontSize) * 1.6 + parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
        if (bt.offsetHeight > one) out.push({ d, type: 'BOUTON', msg: 'le bouton « ' + txt(bt) + ' » tient sur 2 lignes : 22 caractères maximum' });
      });
      const trio = sec.querySelector('.trio');
      if (trio && !sec.classList.contains('sum')) {
        const n = trio.querySelectorAll(':scope > .card').length, want = trio.classList.contains('quad') ? 4 : 3;
        if (n !== want) out.push({ d, type: 'NOMBRE', msg: n + ' cartes dans .trio' + (want === 4 ? '.quad' : '') + ', il en faut ' + want });
      }
      if (sec.classList.contains('side5')) {
        sec.querySelectorAll('.card.pic .stack').forEach(st => {
          if (st.offsetHeight > parseFloat(getComputedStyle(st).minHeight) + 1) out.push({ d, type: 'ALIGNEMENT', msg: 'carte « ' + txt(st).slice(0, 30) + ' » : titre + texte trop longs, les photos ne sont plus alignées (titre 28 car. max sur 2 lignes, texte 80 car. max)' });
        });
        const n = sec.querySelectorAll('.card.pic').length;
        if (n !== 5) out.push({ d, type: 'NOMBRE', msg: n + ' cartes photo dans G04, il en faut 5' });
      }
      const rows = sec.querySelectorAll('.list .row').length;
      if (sec.querySelector('.list') && (rows < 3 || rows > 5)) out.push({ d, type: 'NOMBRE', msg: rows + ' lignes dans la liste G05, il en faut entre 3 et 5' });
    });
    return { n: pages.length, out };
  });

  const secs = page.locator('body > section.page');
  for (let i = 0; i < report.n; i++) await secs.nth(i).screenshot({ path: path.join(outDir, 'diapo-' + String(i + 1).padStart(2, '0') + '.png') });

  const tel = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await tel.goto('file://' + abs);
  await tel.evaluate(() => document.fonts.ready);
  await tel.waitForTimeout(300);
  await tel.screenshot({ path: path.join(outDir, 'telephone.png'), fullPage: true });
  const hs = await tel.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  if (hs) report.out.push({ d: 0, type: 'TÉLÉPHONE', msg: 'la page est plus large que l\'écran du téléphone' });
  await browser.close();

  console.log(report.n + ' diapo(s) capturée(s) dans ' + path.relative(process.cwd(), outDir));
  if (!report.out.length) { console.log('AUCUN PROBLÈME.'); process.exit(0); }
  console.log(report.out.length + ' PROBLÈME(S) :');
  for (const p of report.out) console.log('  ' + (p.d ? 'diapo ' + String(p.d).padStart(2, '0') : 'général ') + '  ' + p.type.padEnd(9) + '  ' + p.msg);
  process.exit(1);
})();
