# Kit Propositions Studio Récitales

Tout ce qu'il faut pour fabriquer des propositions commerciales au design Studio Récitales
(document web, PDF et carrousels Instagram), sans savoir faire de design.

## À donner à Antigravity (Gemini)

1. Donne-lui ce dossier entier.
2. Colle-lui le texte de `PROMPT_A_COLLER.md`, en remplissant la partie « Ce que je veux ».
3. Il doit lire `INSTRUCTIONS_ANTIGRAVITY.md` en entier : c'est le manuel pas à pas.

## Ce qu'il y a dans le dossier

| Dossier / fichier | Contenu |
|---|---|
| `INSTRUCTIONS_ANTIGRAVITY.md` | Le manuel complet : règles, gabarits, limites de caractères mesurées, variantes, images, quoi faire si ça ne rentre pas, mesures en px et mm |
| `PROMPT_A_COLLER.md` | Le message à coller dans Antigravity pour lancer un nouveau document |
| `MODELE_tous_les_gabarits.html` | Les 8 gabarits avec le nom de chaque emplacement écrit dedans (à ouvrir dans un navigateur) |
| `gabarits/` | Les 8 gabarits à copier-coller (G01 à G08) et le squelette de page (G00) |
| `reference/` | Captures de chaque gabarit : emplacements, exemple réel, rendu Instagram et téléphone |
| `exemples/offre-decouverte/` | La proposition « Offre Découverte » complète : source, photos, fichier final |
| `exemples/variantes/` | Exemples des variantes G02 et G03 à 4 cartes |
| `exemples/catalogue-emplacements/` | Source du modèle avec les noms d'emplacements |
| `assets/css/recitales.css` | Tout le design (couleurs, tailles, marges, maquettes de téléphone et de navigateur). Ne pas modifier. |
| `assets/css/polices.css`, `assets/fonts/` | Police Schibsted Grotesk (licence libre SIL OFL) |
| `assets/logo/` | Logo Studio Récitales |
| `assets/placeholders/` | Images grises d'exemple |
| `outils/construire.py` | Assemble la source en un fichier HTML autonome (polices, logo et photos inclus) |
| `outils/verifier.js` | Capture chaque diapo et signale tout texte qui déborde |
| `outils/exporter.js` | Fabrique le PDF et les carrousels Instagram (PNG 1080 × 1350, prix retirés) |
| `outils/archives_claude/` | Les scripts d'origine utilisés pour l'Offre Découverte (pour mémoire) |
| `projets/` | Dossier où créer les nouveaux documents |

## Les trois commandes

```
python3 outils/construire.py projets/NOM/source.html projets/NOM/NOM.html
node outils/verifier.js projets/NOM/NOM.html
node outils/exporter.js projets/NOM/NOM.html
```

Installation (une fois) : Python 3 avec `pip install Pillow`, Node.js, puis dans `outils/` : `npm install` et `npx playwright install chromium`.
