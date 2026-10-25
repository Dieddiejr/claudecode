/*
  exporter.js : fabrique le PDF et les carrousels Instagram d'une proposition construite.

      node outils/exporter.js projets/MON-PROJET/proposition.html

  Produit, dans projets/MON-PROJET/export/ :
    proposition.pdf                       une page par diapo, 1920 x 1080 px
    instagram/01-accroche/01.png ...      un dossier par diapo (= un carrousel),
                                          une image PNG 1080 x 1350 par carte (= un bloc)

  Règles Instagram, écrites dans le HTML (voir INSTRUCTIONS_ANTIGRAVITY.md, étape 7) :
    <section ... data-nom="notre-format">  nom du dossier du carrousel
    <section ... data-insta="non">         cette diapo n'a pas de carrousel
    <... data-insta="masquer">             cet élément n'apparaît pas sur Instagram (ex. un prix)
    <... data-insta-texte="Autre texte">   ce texte remplace celui de l'élément sur Instagram
*/
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const file = process.argv[2];
if (!file || !fs.existsSync(file)) { console.error('Usage : node outils/exporter.js chemin/vers/proposition.html'); process.exit(2); }
const abs = path.resolve(file);
const base = path.basename(abs, '.html');
const outDir = path.join(path.dirname(abs), 'export');
const igDir = path.join(outDir, 'instagram');
fs.rmSync(igDir, { recursive: true, force: true });
fs.mkdirSync(igDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();

  // ---------- PDF ----------
  const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + abs);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  const pdf = path.join(outDir, base + '.pdf');
  await p.pdf({ path: pdf, width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  await p.close();
  console.log('PDF : ' + path.relative(process.cwd(), pdf));

  // ---------- Carrousels Instagram ----------
  // La page est affichée en largeur téléphone (432 px x 2,5 = 1080 px) : chaque carte est
  // posée seule dans un cadre 432 x 540 (= 1080 x 1350) avec 16 px (= 40 px) de marge blanche.
  const q = await browser.newPage({ viewport: { width: 432, height: 540 }, deviceScaleFactor: 2.5 });
  await q.goto('file://' + abs);
  await q.evaluate(() => document.fonts.ready);
  await q.waitForTimeout(400);
  await q.addStyleTag({ content: `
    body>section.page:not(.ig){display:none}
    section.ig{width:432px;height:540px;padding:16px;box-sizing:border-box;overflow:hidden;background:#fff}
    .ig .in{height:100%;padding:0;display:flex}
    .ig .trio{display:flex;flex:1;min-height:0}
    .ig .card{flex:1;height:100%;min-height:0}
    .ig .vis{flex:1 1 auto;height:auto;aspect-ratio:auto;min-height:0}
    .ig .side-ph,.ig .intro-ph{flex:1 1 auto;aspect-ratio:auto;height:auto;min-height:0}
    .ig .row{padding:0;flex:1;align-content:center;row-gap:1vw}
    .ig .row .t{font-size:5.2vw}
    .ig .row .d{font-size:3.7vw;line-height:1.35}
  `});
  const plan = await q.evaluate(() => [...document.querySelectorAll('body>section.page')].map((s, i) => ({
    n: s.querySelectorAll(':scope>.in>.card, :scope>.in>.trio>.card').length,
    nom: s.dataset.nom || 'diapo', skip: s.dataset.insta === 'non' })));
  const problems = [];
  let k = 0;
  for (let i = 0; i < plan.length; i++) {
    if (plan[i].skip) continue;
    k++;
    const dir = path.join(igDir, String(k).padStart(2, '0') + '-' + plan[i].nom);
    fs.mkdirSync(dir, { recursive: true });
    for (let j = 0; j < plan[i].n; j++) {
      const over = await q.evaluate(([i, j]) => {
        document.querySelectorAll('section.ig').forEach(n => n.remove());
        const sec = document.querySelectorAll('body>section.page')[i];
        const card = sec.querySelectorAll(':scope>.in>.card, :scope>.in>.trio>.card')[j];
        const ns = sec.cloneNode(false); ns.classList.add('ig');
        const nin = sec.querySelector(':scope>.in').cloneNode(false); ns.appendChild(nin);
        let host = nin;
        if (card.parentElement.classList.contains('trio')) { host = card.parentElement.cloneNode(false); nin.appendChild(host); }
        const c = card.cloneNode(true); host.appendChild(c);
        c.querySelectorAll('[data-insta="masquer"]').forEach(n => n.remove());
        c.querySelectorAll('[data-insta-texte]').forEach(n => { n.innerHTML = n.getAttribute('data-insta-texte'); });
        document.body.prepend(ns);
        const r = c.getBoundingClientRect();
        const box = ns.getBoundingClientRect();
        if (r.bottom > box.bottom + 1) return true;
        const tel = c.querySelector('.cover-tel');
        if (tel && tel.getBoundingClientRect().top > r.bottom - r.height * 0.4) return true;
        const textRight = n => { const g = document.createRange(); g.selectNodeContents(n); return g.getBoundingClientRect().right; };
        return [...c.querySelectorAll('p,h1,h2,span.label,.stack,.row,.vis,figure,a.btn')]
          .filter(n => !n.closest('.cover-tel') && !(n.closest('.fx') && n.tagName !== 'FIGURE'))
          .some(n => { const b = n.getBoundingClientRect(); return b.bottom > r.bottom + 1 || b.right > r.right + 1 ||
            (/^(P|H1|H2|SPAN)$/.test(n.tagName) && textRight(n) > r.right - parseFloat(getComputedStyle(c).paddingRight) / 2); });
      }, [i, j]);
      await q.waitForTimeout(120);
      const png = path.join(dir, String(j + 1).padStart(2, '0') + '.png');
      await q.locator('section.ig').screenshot({ path: png });
      if (over) problems.push(path.relative(process.cwd(), png));
    }
    console.log('Carrousel : ' + path.relative(process.cwd(), dir) + ' (' + plan[i].n + ' images)');
  }
  await browser.close();
  if (problems.length) {
    console.log('ATTENTION, texte qui déborde sur Instagram (ou téléphone de couverture presque caché) :');
    problems.forEach(p => console.log('   ' + p));
    console.log('Raccourcis le texte de ces cartes (voir INSTRUCTIONS_ANTIGRAVITY.md, partie 9).');
    process.exit(1);
  }
  console.log('AUCUN PROBLÈME.');
})();
