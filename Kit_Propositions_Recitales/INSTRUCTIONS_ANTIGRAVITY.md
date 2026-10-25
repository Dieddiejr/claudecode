# MANUEL : fabriquer une proposition Studio Récitales

Ce manuel s'adresse à l'agent qui fabrique les documents (Antigravity / Gemini).
Lis-le EN ENTIER avant de commencer. Suis les étapes DANS L'ORDRE. Ne saute aucune étape.

Tu ne fais PAS de design. Le design est déjà fait et réglé au pixel près dans `assets/css/recitales.css`.
Ton travail : **choisir des gabarits, les copier, remplacer les emplacements `[[...]]` par du texte, mettre les photos, lancer les trois commandes, corriger ce que les commandes signalent.**

---

## 0. RÈGLES ABSOLUES (à relire avant chaque document)

1. **Ne modifie JAMAIS** `assets/css/recitales.css`, `assets/css/polices.css`, ni les fichiers du dossier `outils/`.
2. **N'écris JAMAIS de CSS.** Pas de balise `<style>`, pas d'attribut `style="..."`.
   SEULE exception autorisée : la valeur de `object-position` sur une balise `<img>` (voir partie 6.4), et la largeur `width:..cqw` déjà écrite sur les `<figure>` (tu ne la changes pas).
3. **N'invente AUCUNE classe.** Les seules classes autorisées sont celles qui sont déjà dans les gabarits, plus les variantes écrites en partie 5.
4. **Ne change pas l'ordre des balises d'un gabarit.** Tu remplaces le texte, tu ne déplaces rien.
5. **N'ajoute pas de carte, de colonne, de ligne ou d'image** dans un gabarit, sauf avec une variante de la partie 5.
6. **Pas de gras** (`<b>`, `<strong>`), **pas d'italique**, **pas de souligné**, **pas d'émoji**, **pas de MAJUSCULES** dans les textes (les étiquettes passent toutes seules en majuscules).
7. **Respecte les limites de caractères** de la partie 4. Elles ont été mesurées : au-delà, le texte sort de la carte.
8. **Une diapo = un gabarit entier**, de `<section` à `</section>`.
9. **Après chaque modification**, relance `construire.py` puis `verifier.js` (partie 8). Un document n'est terminé que quand `verifier.js` affiche `AUCUN PROBLÈME.` ET `exporter.js` affiche `AUCUN PROBLÈME.`
10. **Pas de prix sur Instagram.** Tout prix est marqué pour disparaître des carrousels (partie 7).
11. Si une situation n'est pas prévue dans ce manuel : **arrête-toi et pose la question** à l'utilisateur. N'improvise pas.

---

## 1. INSTALLATION (une seule fois par ordinateur)

Ouvre un terminal dans le dossier `Kit_Propositions_Recitales` et tape :

```
pip install Pillow
cd outils
npm install
npx playwright install chromium
cd ..
```

Sur Windows, écris `python` au lieu de `python3` dans TOUTES les commandes de ce manuel.

Vérifie : `python3 outils/construire.py exemples/offre-decouverte/source.html exemples/offre-decouverte/offre-decouverte.html` doit afficher `OK : ...`.

---

## 2. CRÉER UN NOUVEAU PROJET

Exemple pour un projet appelé `atelier-dupont` (nom en minuscules, sans accent, mots séparés par des tirets) :

1. Crée le dossier `projets/atelier-dupont/`.
2. Crée le dossier `projets/atelier-dupont/images/`.
3. Copie `gabarits/G00_squelette.html` vers `projets/atelier-dupont/source.html`.
4. Dans `source.html`, remplace `[[TITRE_DU_DOCUMENT]]` par le titre de l'onglet du navigateur (2 à 5 mots, ex. `Proposition Atelier Dupont`).
5. Range toutes les photos dans `projets/atelier-dupont/images/` (règles de nommage en partie 6.1).

Le fichier `source.html` ne contient que :
```html
<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proposition Atelier Dupont</title>
<!-- STYLES DU KIT -->
</head>
<body>

<!-- COLLER LES DIAPOS ICI, DANS L'ORDRE, LES UNES SOUS LES AUTRES -->

</body></html>
```
Ne supprime JAMAIS la ligne `<!-- STYLES DU KIT -->` : `construire.py` la remplace par le design.

---

## 3. CHOISIR LES GABARITS

### 3.1 Les 8 gabarits

Regarde les images dans `reference/` : `Gxx__emplacements.png` montre où va chaque emplacement, `Gxx__exemple.png` montre le résultat avec de vrais textes.

| Gabarit | Fichier | Sert à | Images à fournir |
|---|---|---|---|
| G01 | `gabarits/G01_couverture.html` | Première diapo : une question d'accroche, une promesse, le prix | 1 verticale 9:16 |
| G02 | `gabarits/G02_introduction.html` | Un mot d'introduction en deux paragraphes | 1 paysage 16:10 ou 3:2 |
| G03 | `gabarits/G03_trois_cartes.html` | Expliquer 3 choses (étapes, format, réalisations) | 3 portrait 4:5 |
| G04 | `gabarits/G04_cinq_cartes.html` | Montrer 5 choses avec 5 photos | 5 portrait 4:5 ou 3:4 |
| G05 | `gabarits/G05_liste.html` | Une liste numérotée de 3 à 5 points | 1 paysage 16:10 (facultative) |
| G06 | `gabarits/G06_instagram.html` | Montrer le résultat sur un compte Instagram | 12 petites portrait + 1 verticale 9:16 |
| G07 | `gabarits/G07_capture_site.html` | Montrer une page de site web | 1 capture d'écran 16:10 |
| G08 | `gabarits/G08_resume_contact.html` | Dernière diapo : résumé de l'offre, prix, contact | aucune |

### 3.2 Quel gabarit pour quel contenu (applique la PREMIÈRE ligne qui correspond)

| Le contenu à présenter, c'est... | Gabarit |
|---|---|
| La toute première diapo du document | G01 (toujours) |
| La toute dernière diapo du document | G08 (toujours) |
| Un texte de présentation de 1 ou 2 paragraphes, sans liste | G02 |
| Exactement 3 éléments, chacun avec une photo | G03 |
| Exactement 4 éléments, chacun avec une photo | G03 variante B (4 cartes) |
| Exactement 5 éléments, chacun avec une photo | G04 |
| 3, 4 ou 5 éléments SANS photo chacun | G05 |
| 6 à 10 éléments | DEUX diapos G05 à la suite (partie 9.3) |
| Des personnes ou entreprises déjà filmées (portfolio) | G03 variante A (réalisations) |
| Le rendu sur Instagram | G06 |
| Le site web de Studio Récitales ou du client | G07 |
| 2 éléments seulement | G05 n'est PAS autorisé (3 lignes minimum) : demande un 3e élément à l'utilisateur, ou mets ces 2 éléments dans un G02 |

### 3.3 Plan type d'une proposition (à suivre sauf demande contraire)

| Ordre | Gabarit | Contenu |
|---|---|---|
| 1 | G01 | Accroche (question au client) + promesse + prix |
| 2 | G03 (variante C si on veut montrer un téléphone) | Notre format : comment ça se passe, en 3 temps |
| 3 | G04 ou G05 | Ce que le client reçoit (les vidéos, les contenus) |
| 4 | G05 | Ce que le client reçoit (suite) ou les bénéfices |
| 5 | G06 | Le résultat sur Instagram |
| 6 | G07 avec logo | Qui nous sommes (capture de la page d'accueil) |
| 7 | G07 sans logo (variante) | Nos services (capture de la page services) |
| 8 | G03 variante A | Nos réalisations |
| 9 | G08 | L'offre en résumé + contact |

Minimum : 4 diapos (G01, une diapo de contenu, G03 réalisations, G08). Maximum : 12 diapos.

### 3.4 Coller un gabarit

1. Ouvre le fichier du gabarit (ex. `gabarits/G03_trois_cartes.html`).
2. Copie TOUT, de la ligne `<section` jusqu'à la ligne `</section>` incluse. Ne copie pas le grand commentaire `<!-- ===== ... ===== -->` du haut (tu peux, mais c'est inutile).
3. Dans `source.html`, colle JUSTE AU-DESSUS de la ligne `<!-- COLLER LES DIAPOS ICI... -->`.
4. Ajoute au-dessus de ta `<section` un commentaire de repère : `<!-- Diapo 3 : ce que vous recevez -->`.
5. Recommence pour la diapo suivante : elle se colle aussi juste au-dessus de la ligne repère, donc APRÈS la précédente.

---

## 4. REMPLIR LES TEXTES

### 4.1 Règles d'écriture (pour TOUS les emplacements)

| Règle | Écris | N'écris pas |
|---|---|---|
| Apostrophe typographique | `L’échange` (caractère ’) | `L'échange` |
| Espace insécable avant `? ! : ;` | `les fêtes&nbsp;?` | `les fêtes ?` ou `les fêtes?` |
| Espace insécable avant `€` et `%` | `100&nbsp;€` | `100 €` ou `100€` |
| Espace insécable entre un nombre et son mot | `10&nbsp;vidéos`, `2&nbsp;heures` | `10 vidéos` |
| Guillemets français | `«&nbsp;mot&nbsp;»` | `"mot"` |
| Les GRANDS titres (`<h2>`) finissent par un point | `Notre format.` | `Notre format` |
| Les titres de carte (`<p class="s">`, `<p class="t">`) ne finissent PAS par un point | `L’échange` | `L’échange.` |
| Les textes courants (`<p class="x">`, `<p class="d">`) sont des phrases avec un point final | `On vous filme en action.` | `on vous filme en action` |
| Retour à la ligne forcé `<br>` | UNIQUEMENT dans G03 variante A (texte sous le nom) et dans le bloc contact de G08 | partout ailleurs |
| Vouvoiement | `vous`, `votre` | `tu`, `ton` |
| Caractères `<` `>` `&` dans un texte | `&lt;` `&gt;` `&amp;` | `<` `>` `&` |

### 4.2 Comment compter

- On compte TOUS les caractères, espaces et ponctuation compris. `&nbsp;` compte pour 1. `’` compte pour 1.
- « Mot le plus long » = le nombre de lettres du plus long mot du texte. Si un mot dépasse, la partie 9.2 dit quoi faire.
- Les limites viennent de mesures : au-delà, le texte sort de la carte dans le PDF ou dans les images Instagram.

### 4.3 G01 · Couverture

Voir `reference/G01_couverture__emplacements.png` et `reference/G01_couverture__exemple.png`.

| Emplacement | Ce qu'on y met | Max caractères | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G01_ETIQUETTE]]` | Nom de l'offre, 1 à 3 mots | 22 | 13 | `Offre Découverte` |
| `[[G01_QUESTION]]` | Une question posée au client, finit par `&nbsp;?` | 90 | 13 | `Vous préparez une nouveauté, une promo ou une offre spéciale pour les fêtes&nbsp;?` |
| `[[G01_PROMESSE]]` | Ce qu'on fait pour lui, une phrase, finit par un point | 40 | 16 | `On vous aide à la faire découvrir.` |
| `[[G01_DETAIL]]` | Le concret de l'offre, SANS le prix, finit par `pour` | 40 | 13 | `10&nbsp;vidéos tournées chez vous en 2&nbsp;heures, pour` |
| `[[G01_PRIX]]` | Le prix seul | 10 | – | `100&nbsp;€` |
| `[[G01_DETAIL_INSTAGRAM]]` | La même phrase que G01_DETAIL, SANS « pour » et SANS prix, finie par un point | 45 | 13 | `10&nbsp;vidéos tournées chez vous en 2&nbsp;heures.` |
| `[[G01_COMPTE]]` | Nom de compte Instagram du client, minuscules, sans espace | 20 | – | `votre_compte` |
| `[[G01_LEGENDE]]` | Légende du Reel | 45 | – | `Notre nouveauté pour les fêtes` |
| `[[G01_PHOTO_DESCRIPTION]]` | Description invisible de la photo (accessibilité) | 80 | – | `Samuel Perraro dans son atelier` |

G01_DETAIL + G01_PRIX ensemble : 50 caractères maximum. Pas de prix ? → variante G01-SANS-PRIX (partie 5.1).

### 4.4 G02 · Introduction

| Emplacement | Ce qu'on y met | Max | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G02_TEXTE_GAUCHE]]` | Qui on est, ce qu'on fait en ce moment | 180 | 19 | `Actuellement je chemine dans toute la région pour faire des portraits de gens qui ont leur activité sur notre territoire régional.` |
| `[[G02_TEXTE_DROITE]]` | Ce qu'on propose au client | 220 | 19 | `J’aimerais vous proposer de faire les portraits de dix activités que vous accompagnez. Je me déplacerai à mes frais pour aller à leur rencontre et mettre en valeur leur activité.` |
| `[[G02_PHOTO_DESCRIPTION]]` | Description invisible de la photo | 80 | – | `Samuel Perraro, céramiste` |

### 4.5 G03 · Trois cartes photo

| Emplacement | Ce qu'on y met | Max | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G03_INTRO]]` | Une phrase qui résume la diapo | 150 | 19 | `On vient à votre rencontre pendant deux heures pour présenter votre activité, ce que vous proposez, et le mettre en valeur.` |
| `[[G03_TITRE]]` | Grand titre, 1 à 3 mots, finit par un point | 30 | 12 | `Notre format.` |
| `[[G03_C1_TITRE]]` `[[G03_C2_TITRE]]` `[[G03_C3_TITRE]]` | Titre de chaque carte, 1 à 4 mots | 30 | 19 | `L’échange` |
| `[[G03_C1_TEXTE]]` `[[G03_C2_TEXTE]]` `[[G03_C3_TEXTE]]` | Une ou deux phrases | 110 | 19 | `Vous nous parlez de votre projet et de ce que vous préparez pour les fêtes.` |
| `[[G03_Cn_PHOTO_DESCRIPTION]]` | Description invisible de chaque photo | 80 | – | `Interview filmée` |

Les 3 titres de carte doivent avoir une longueur proche (écart de 15 caractères maximum entre le plus court et le plus long).

### 4.6 G04 · Cinq cartes photo

| Emplacement | Ce qu'on y met | Max | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G04_INTRO]]` | Une phrase | 70 | 13 | `Cinq vidéos pour faire découvrir ce que vous préparez.` |
| `[[G04_TITRE]]` | Grand titre, finit par un point | 20 | **9** | `Pour les fêtes.` |
| `[[G04_C1_TITRE]]` à `[[G04_C5_TITRE]]` | Titre de chaque carte (2 lignes max) | 28 | 13 | `Votre offre ou votre promo` |
| `[[G04_C1_TEXTE]]` à `[[G04_C5_TEXTE]]` | Une phrase | 80 | 13 | `Horaires, dates limites, comment commander ou réserver.` |
| `[[G04_Cn_PHOTO_DESCRIPTION]]` | Description invisible | 80 | – | `Mélissa Beynet face caméra` |

ATTENTION G04_TITRE : la carte est étroite, AUCUN mot de plus de 9 lettres (`activités` = 9 : OK ; `découverte` = 10 : INTERDIT).

### 4.7 G05 · Liste numérotée

| Emplacement | Ce qu'on y met | Max | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G05_ETIQUETTE]]` | 1 à 3 mots | 22 | 13 | `Cinq vidéos` |
| `[[G05_TITRE]]` | Grand titre, finit par un point | 30 | 12 | `Pour votre activité.` |
| `[[G05_SOUS_TITRE]]` | Une phrase | 60 | 19 | `Elles servent bien après les fêtes.` |
| `[[G05_L1_TITRE]]` à `[[G05_L5_TITRE]]` | Titre de la ligne, sur UNE ligne | 28 | 19 | `Vous, derrière le projet` |
| `[[G05_L1_TEXTE]]` à `[[G05_L5_TEXTE]]` | Une ou deux phrases courtes | 85 | 19 | `Vos gestes, vos outils. Le client voit comment ça se passe avant d’acheter.` |
| `[[G05_PHOTO_DESCRIPTION]]` | Description invisible | 80 | – | `Les mains de Samuel Perraro` |

Les numéros `01` à `05` sont écrits dans `<span class="n">`. Si cette liste continue une liste précédente, renumérote : `06`, `07`, `08`, `09`, `10`. Toujours 2 chiffres.

### 4.8 G06 · Instagram

| Emplacement | Ce qu'on y met | Max | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G06_ETIQUETTE]]` | 1 à 3 mots | 22 | 13 | `Sur votre compte` |
| `[[G06_TITRE]]` | Une phrase-titre, finit par un point | 60 | 13 | `Tout ce que vous préparez pour les fêtes, en vidéo.` |
| `[[G06_TEXTE]]` | Une phrase | 90 | 19 | `Votre offre et votre activité, visibles dès qu’on ouvre votre profil.` |
| `[[G06_COMPTE]]` (écrit 2 fois, même valeur) | Nom du compte | 20 | – | `votre_compte` |
| `[[G06_PUBLICATIONS]]` `[[G06_FOLLOWERS]]` `[[G06_SUIVIS]]` | Nombres, espace entre les milliers | 6 | – | `128`, `1 240`, `312` |
| `[[G06_NOM]]` | Nom affiché du compte | 25 | – | `Votre activité` |
| `[[G06_BIO]]` | Bio du compte | 45 | – | `Nos nouveautés et nos offres pour les fêtes` |
| `[[G06_LEGENDE]]` | Légende du Reel | 50 | – | `Notre offre des fêtes, expliquée en une minute` |
| `[[G06_PHOTO_DESCRIPTION]]` | Description invisible du Reel | 80 | – | `Caroline Dinet au travail` |

### 4.9 G07 · Capture de site

| Emplacement | Ce qu'on y met | Max | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G07_TITRE]]` | Grand titre, finit par un point | 30 | 12 | `Qui nous sommes.` |
| `[[G07_ADRESSE]]` | Adresse de la page, SANS `https://` ni `www.` | 40 | – | `studiorecitales.fr/services` |
| `[[G07_PHOTO_DESCRIPTION]]` | Description invisible | 80 | – | `Page d’accueil du site Studio Récitales` |

### 4.10 G08 · Résumé et contact

| Emplacement | Ce qu'on y met | Max | Mot le plus long | Exemple validé |
|---|---|---|---|---|
| `[[G08_TITRE]]` | Grand titre, finit par un point | 30 | 12 | `L’offre en résumé.` |
| `[[G08_ETIQUETTE]]` | Nom de l'offre (le même que G01_ETIQUETTE) | 22 | 13 | `Offre Découverte` |
| `[[G08_POINT_1]]` | Ce que le client reçoit, finit par un point | 30 | 12 | `Dix vidéos.` |
| `[[G08_POINT_1_DETAIL]]` | Précision, une phrase | 70 | 19 | `Cinq pour les fêtes, cinq pour votre activité.` |
| `[[G08_PRIX]]` | Le prix seul (le même que G01_PRIX) | 8 | – | `100&nbsp;€` |
| `[[G08_POINT_2]]` | Deuxième point fort, finit par un point | 30 | 12 | `Deux heures chez vous.` |
| `[[G08_POINT_2_DETAIL]]` | Précision, une phrase | 70 | 19 | `Déplacement inclus.` |
| `[[G08_NOM]]` | Nom du studio | 30 | – | `Studio Récitales` |
| `[[G08_TELEPHONE]]` | Numéro affiché, par paires | – | – | `06 75 14 68 71` |
| `[[G08_TELEPHONE_LIEN]]` | Même numéro au format international, sans espace | – | – | `+33675146871` |
| `[[G08_EMAIL]]` (écrit 3 fois, même valeur) | Adresse e-mail | – | – | `hello@studiorecitales.fr` |
| `[[G08_SITE]]` (écrit 2 fois) | Site, SANS `https://` ni `www.` | – | – | `studiorecitales.fr` |
| `[[G08_SUJET_EMAIL]]` | Objet du mail du bouton, encodé pour une adresse web : espace = `%20`, é = `%C3%A9`, è = `%C3%A8`, ê = `%C3%AA`, à = `%C3%A0`, ç = `%C3%A7` | – | – | `Offre%20D%C3%A9couverte%20f%C3%AAtes` |
| `[[G08_BOUTON]]` | Texte du bouton, verbe à l'infinitif, sur UNE ligne | 22 | – | `Réserver mon tournage` |

Coordonnées actuelles de Studio Récitales (à utiliser sauf indication contraire) : `Studio Récitales`, `06 75 14 68 71`, `+33675146871`, `hello@studiorecitales.fr`, `studiorecitales.fr`.

---

## 5. VARIANTES (blocs de code exacts à copier)

Une variante = un remplacement précis dans un gabarit déjà collé. Fais EXACTEMENT le remplacement écrit, rien d'autre.

### 5.1 G01-SANS-PRIX (pas de prix dans l'offre)

Remplace la ligne :
```html
      <p class="cover-sub" data-insta-texte="[[G01_DETAIL_INSTAGRAM]]">[[G01_DETAIL]] <span class="hl">[[G01_PRIX]]</span>.</p>
```
par :
```html
      <p class="cover-sub">[[G01_DETAIL]]</p>
```
Ici G01_DETAIL est une phrase complète finie par un point, 45 caractères maximum.

### 5.2 G03 variante A : RÉALISATIONS (portfolio)

1. Remplace `<p class="s">[[G03_INTRO]]</p>` par `<span></span>`.
2. Dans chacune des 3 cartes, ajoute ` real` à la classe : `<div class="card g">` devient `<div class="card g real">`, `<div class="card y">` devient `<div class="card y real">`, `<div class="card b">` devient `<div class="card b real">`.
3. `[[G03_Cn_TITRE]]` = nom de la personne ou de l'entreprise (30 max).
4. `[[G03_Cn_TEXTE]]` = 1 ou 2 lignes séparées par `<br>`, 30 caractères max par ligne : `Mélissa Beynet<br>Tufting, Marseille`.
5. Photos : portrait 4:5, la personne en entier ou à mi-corps.
6. `data-nom="trois-cartes"` devient `data-nom="nos-realisations"`.
Résultat attendu : `reference/G03_trois_cartes__exemple_variante_A_realisations.png`.

### 5.3 G03 variante B : QUATRE CARTES

1. Remplace `<div class="trio">` par `<div class="trio quad">`.
2. Juste avant la ligne `  </div>` qui ferme le trio (la ligne qui suit la 3e carte), ajoute cette 4e carte :
```html
    <div class="card g"><div class="vis"><img alt="[[G03_C4_PHOTO_DESCRIPTION]]" src="{{img:@portrait}}" style="object-position:50% 50%"></div><div class="stack"><p class="s">[[G03_C4_TITRE]]</p><p class="x">[[G03_C4_TEXTE]]</p></div></div>
```
3. Limites en 4 cartes : titre de carte 24 caractères, texte de carte 80 caractères, `[[G03_INTRO]]` 120 caractères.
4. Compatible avec la variante A : ajoute alors ` real` aux 4 cartes.
Résultat attendu : `reference/G03_trois_cartes__exemple_variante_B_quatre_cartes.png`.

### 5.4 G03 variante C : TÉLÉPHONE dans la 3e carte (pour montrer une vidéo)

Dans la 3e carte (`<div class="card b">`), remplace :
```html
<div class="vis"><img alt="[[G03_C3_PHOTO_DESCRIPTION]]" src="{{img:@portrait}}" style="object-position:50% 50%"></div>
```
par :
```html
<div class="vis mock"><figure class="fx fx-tel fx-reel" style="width:11cqw"><div class="fx-b"><div class="fx-in"><img alt="[[G03_C3_PHOTO_DESCRIPTION]]" src="{{img:@vertical}}" style="object-position:50% 50%"></div></div></figure></div>
```
La photo doit être VERTICALE 9:16 (une image de vidéo verticale, idéalement avec ses sous-titres).
Résultat attendu : `reference/G03_trois_cartes__exemple_variante_C_telephone.png`.

### 5.5 G05 avec 3 ou 4 lignes

Supprime les lignes `<div class="row">...</div>` en trop EN PARTANT DU BAS (supprime la 5e, puis la 4e). Garde la numérotation continue. Minimum 3 lignes. Ne change rien d'autre : les lignes restantes s'espacent toutes seules.

### 5.6 G05 sans photo

Supprime la ligne entière :
```html
    <div class="side-ph"><img alt="[[G05_PHOTO_DESCRIPTION]]" src="{{img:@paysage}}" style="object-position:50% 50%"></div>
```
L'étiquette reste en haut, le titre et le sous-titre restent en bas.

### 5.7 G07 sans logo (2e capture de site à la suite)

Quand deux G07 se suivent, la 2e n'a pas de logo et change de couleurs :
1. Remplace `<div class="card g between"><div class="logo" role="img" aria-label="Studio Récitales"></div>` par `<div class="card y between"><span></span>`.
2. Remplace `<div class="card y center">` par `<div class="card b center">`.
Résultat attendu : `reference/G07_capture_site__exemple_variante_sans_logo.png`.

### 5.8 G08 sans prix

Supprime la ligne `<p class="s price" data-insta="masquer">[[G08_PRIX]]</p>` (à l'intérieur de la carte bleue). Garde le reste.

---

## 6. LES IMAGES

### 6.1 Ranger et nommer

- Toutes les images d'un projet vont dans `projets/NOM-DU-PROJET/images/`.
- Nom de fichier : minuscules, sans accent, sans espace, mots séparés par des tirets, extension `.jpg` (photos) ou `.png` (logos, captures avec transparence). Exemples : `melissa-portrait.jpg`, `capture-accueil.jpg`.
- Formats acceptés : `.jpg`, `.jpeg`, `.png`, `.webp`. PAS de `.heic` : convertis-le d'abord en `.jpg`.

### 6.2 Mettre une image dans un emplacement

Dans les gabarits, chaque image est écrite `src="{{img:@portrait}}"` (ou `@paysage`, `@vertical`, `@capture`, `@carre`) : c'est une image grise d'exemple.
Remplace `@portrait` par le chemin de ta photo, en partant du dossier du projet :
```html
<img alt="Mélissa Beynet face caméra" src="{{img:images/melissa-interview.jpg}}" style="object-position:50% 50%">
```
Garde `|300` s'il est présent (grille Instagram de G06) : `{{img:images/tuile-01.jpg|300}}`.

### 6.3 Quelle forme de photo pour quel emplacement

| Emplacement | Forme demandée | Si tu n'as qu'une photo d'une autre forme |
|---|---|---|
| G01 téléphone, G06 Reel, G03 variante C | VERTICALE 9:16 (debout, très haute) | Une photo portrait 4:5 marche : règle `object-position` sur le visage. Une photo paysage NE marche PAS : demande une autre photo. |
| G03, G04 cartes | PORTRAIT 4:5 ou 3:4 | Paysage accepté si le sujet est au centre : règle `object-position`. |
| G03 variante A (réalisations) | PORTRAIT 4:5 | Pareil. |
| G02, G05 | PAYSAGE 16:10 ou 3:2 | Portrait refusé (trop recadré). |
| G06 grille (12 cases) | PORTRAIT 3:4, même petites | On peut répéter les mêmes photos (12 cases à remplir obligatoirement). |
| G07 | CAPTURE d'écran d'ordinateur, 16:10, au moins 1600 px de large | Le haut de la page est gardé, le bas est coupé. |

Taille minimale d'une photo : 800 px de large (300 px pour la grille G06). Plus petite : elle sera floue, demande une meilleure photo.
Taille maximale : aucune. `construire.py` réduit automatiquement à 1600 px de large. Ne réduis rien toi-même.

### 6.4 Cadrage : la valeur `object-position`

Les photos remplissent toujours leur cadre et sont recadrées automatiquement. `object-position` dit QUELLE partie de la photo garder. Première valeur = horizontale (0% gauche, 100% droite), deuxième = verticale (0% haut, 100% bas).

| Où est le sujet (le visage, l'objet) dans la photo d'origine | Valeur à écrire |
|---|---|
| Au centre (cas par défaut) | `object-position:50% 50%` |
| À gauche | `object-position:25% 50%` |
| À droite | `object-position:75% 50%` |
| En haut (visage en haut d'une photo en pied) | `object-position:50% 25%` |
| En bas | `object-position:50% 75%` |
| En haut à gauche | `object-position:25% 25%` |
| En haut à droite | `object-position:75% 25%` |
| Capture de site (G07) | `object-position:50% 0` (toujours) |

Après `verifier.js`, ouvre la capture `controle/diapo-XX.png` : si un visage est coupé, déplace la valeur de 10% vers le côté coupé et recommence.

### 6.5 Choisir les photos (dans l'ordre de priorité)

1. Une personne qui travaille avec ses mains, ou qui regarde l'objectif.
2. Pas de photo floue, sombre, ou avec un texte incrusté illisible.
3. Dans un même gabarit, pas deux fois la même photo (sauf la grille G06).
4. Les photos d'une même diapo viennent si possible du même tournage (mêmes couleurs).
5. Ne mets jamais une personne qui n'est pas autorisée par l'utilisateur. En cas de doute : demande.

---

## 7. INSTAGRAM : CE QUI CHANGE DANS LES CARROUSELS

`exporter.js` fabrique un carrousel par diapo, une image PNG 1080 × 1350 par carte. Tu le règles avec 4 attributs, déjà présents dans les gabarits :

| Attribut | Où | Effet | Déjà réglé dans |
|---|---|---|---|
| `data-nom="notre-format"` | sur `<section>` | Nom du dossier du carrousel (`03-notre-format/`). Minuscules, tirets, sans accent. Change-le pour chaque diapo. | toutes les sections |
| `data-insta="non"` | sur `<section>` | Pas de carrousel pour cette diapo | à ajouter si l'utilisateur le demande |
| `data-insta="masquer"` | sur un élément | L'élément disparaît sur Instagram | le prix de G08 |
| `data-insta-texte="..."` | sur un élément | Ce texte remplace le texte de l'élément sur Instagram | la phrase prix de G01 (remplacée par G01_DETAIL_INSTAGRAM) |

RÈGLE : **aucun prix sur Instagram.** Si tu écris un prix ailleurs que dans `[[G01_PRIX]]` ou `[[G08_PRIX]]`, ajoute `data-insta="masquer"` sur la balise qui le contient, ou `data-insta-texte="même phrase sans le prix"`.

---

## 8. CONSTRUIRE, VÉRIFIER, EXPORTER

Lance les commandes depuis le dossier `Kit_Propositions_Recitales`.

### 8.1 Construire
```
python3 outils/construire.py projets/atelier-dupont/source.html projets/atelier-dupont/atelier-dupont.html
```
- `OK : ...` → continue.
- `ERREUR : ces emplacements n'ont pas été remplacés` → remplace les `[[...]]` listés.
- `ERREUR : images introuvables` → vérifie le nom du fichier et le dossier `images/`.
- `ATTENTION : image(s) d'exemple grise(s)` → il reste des `@portrait`, `@paysage`... : mets les vraies photos.

### 8.2 Vérifier
```
node outils/verifier.js projets/atelier-dupont/atelier-dupont.html
```
Ouvre ensuite CHAQUE image `projets/atelier-dupont/controle/diapo-XX.png` et compare-la avec `reference/Gxx__exemple.png` du même gabarit. Elles doivent se ressembler : mêmes positions, mêmes tailles de texte.

### 8.3 Exporter
```
node outils/exporter.js projets/atelier-dupont/atelier-dupont.html
```
Produit `projets/atelier-dupont/export/atelier-dupont.pdf` et `projets/atelier-dupont/export/instagram/`. Ouvre au moins la 1re et la dernière image de chaque carrousel.

Pour envoyer les carrousels en un seul fichier :
```
python3 -m zipfile -c projets/atelier-dupont/export/instagram.zip projets/atelier-dupont/export/instagram/
```

### 8.4 Ce que tu livres à l'utilisateur

1. `projets/NOM/NOM.html` (le document web, autonome)
2. `projets/NOM/export/NOM.pdf`
3. `projets/NOM/export/instagram.zip`

---

## 9. QUAND ÇA NE RENTRE PAS : QUOI FAIRE, DANS L'ORDRE

Applique l'option A. Relance `construire.py` + `verifier.js`. Si le problème reste, passe à l'option B, etc.

### 9.1 `DÉBORDE` (texte trop long, carte qui sort de la diapo) ou `ALIGNEMENT`

- A. Raccourcis le texte signalé jusqu'à la limite de la partie 4 (compte les caractères).
- B. Raccourcis encore de 20 %, en enlevant les mots inutiles (« vraiment », « tout à fait », « en effet », adjectifs en double).
- C. Coupe le contenu en deux diapos du même gabarit (ex. deux G05).
- JAMAIS : réduire la taille du texte, changer le CSS, enlever une marge.

### 9.2 Un mot trop long dans un grand titre (`un mot est trop long pour la largeur`)

- A. Remplace le mot par un synonyme plus court qui garde le sens. Exemples : `accompagnement` → `suivi`, `communication` → `visibilité`, `professionnelle` → `pro` (uniquement si le reste du document a ce ton familier), `présentation` → `portrait`.
- B. Pour un `<h2>` de G03, G05, G07 ou G08 uniquement : si le mot fait 13 à 15 lettres, écris `<h2 class="sm">` au lieu de `<h2>` (titre plus petit, prévu dans le design).
- C. Reformule le titre.
- JAMAIS : couper un mot avec un tiret.

### 9.3 Trop d'éléments pour un gabarit

| Tu as | Fais |
|---|---|
| 6 éléments avec photo | G03 (3) + G03 (3), ou G04 (5) en enlevant le moins important : DEMANDE à l'utilisateur lequel enlever |
| 6 à 10 éléments sans photo | 2 diapos G05 : la 1re avec les éléments 1 à 5 (numéros 01 à 05), la 2e avec la suite (06, 07...). La 2e G05 prend les couleurs `card y` (gauche) et `card b` (droite) |
| Plus de 10 éléments | Demande à l'utilisateur de choisir les 10 plus importants |
| Plus de 3 réalisations | G03 variante A + B (4 cartes). Plus de 4 : deux diapos réalisations |
| Plus de 12 photos pour G06 | Garde les 12 plus belles |

### 9.4 Pas assez d'éléments

| Tu as | Fais |
|---|---|
| 1 élément | Mets-le dans G02 (texte de droite) |
| 2 éléments | G02 : un élément par carte |
| 3 éléments sans photo | G05 à 3 lignes (variante 5.5) |
| 4 éléments avec seulement 3 photos | G05 à 4 lignes (avec la meilleure photo en haut à gauche) |
| Moins de 12 photos pour G06 | Répète les photos dans la grille, dans un ordre mélangé, jusqu'à 12 |
| Aucune photo verticale pour G01 | Une photo portrait recadrée (`object-position` sur le visage). Aucune portrait non plus : demande une photo à l'utilisateur |
| Pas de capture de site pour G07 | Supprime la diapo G07 |

### 9.5 Pas d'information pour un emplacement

Ne l'invente pas. Demande-la à l'utilisateur. En attendant, laisse `[[...]]` : `construire.py` refusera de construire, c'est normal.

---

## 10. COULEURS DES CARTES (déjà réglées, à NE PAS changer sauf ici)

Les classes de couleur sont `g` (vert), `y` (jaune), `b` (bleu). Elles sont déjà écrites dans les gabarits. Tu les changes UNIQUEMENT dans ces cas :

| Cas | Carte de gauche | Cartes de droite |
|---|---|---|
| G01 | `g` | `y` |
| G02 | `g` | `y` |
| G03 (toutes variantes) | `b` | `g`, `y`, `b` (+ `g` pour la 4e) |
| G04 | `b` | `g`, `y`, `b`, `g`, `y` |
| G05 (1re) | `g` | `y` |
| G05 (2e à la suite) | `y` | `b` |
| G06 | `b` | `g` |
| G07 avec logo | `g` | `y` |
| G07 sans logo (2e à la suite) | `y` | `b` |
| G08 | `g` | `y`, `b`, `g` |

Valeurs des couleurs (pour information, déjà dans le CSS) :
- vert `g` : dégradé du haut vers le bas `#C6FBAE` → `#E6FBD9` → `#FBFDF8`, texte `#14363A`
- jaune `y` : `#FFF59A` → `#FFF9CC` → `#FFFDF2`, texte `#8A4A1F`
- bleu `b` : `#BFDCFF` → `#E3EDFF` → `#FCEFEF`, texte `#14213D`
- fond de page : blanc `#FFFFFF`. Police : Schibsted Grotesk, poids 400 (texte) et 500 (titres).

---

## 11. LA RÈGLE GRADUÉE (mesures exactes du design)

Tu n'écris JAMAIS ces valeurs : elles sont dans `recitales.css`. Elles servent à VÉRIFIER une capture.
Une diapo PDF mesure 1920 × 1080 px = 508 × 285,75 mm. L'unité du design est `u` (= `cqw`) : **1 u = 1 % de la largeur = 19,2 px = 5,08 mm.**

### 11.1 Mise en page (PDF et écran d'ordinateur)

| Élément | u | px (1920) | mm |
|---|---|---|---|
| Marge blanche autour des cartes | 1,8 | 34,6 | 9,1 |
| Espace entre deux cartes | 1,4 | 26,9 | 7,1 |
| Arrondi des coins des cartes | 1,1 | 21,1 | 5,6 |
| Marge intérieure d'une grande carte | 2,8 | 53,8 | 14,2 |
| Marge intérieure des cartes en série (G03, G08) | 1,6 | 30,7 | 8,1 |
| Marge intérieure des cartes G04 | 1,1 | 21,1 | 5,6 |
| Marge intérieure de la carte titre G04 | 2,2 | 42,2 | 11,2 |
| Écart entre un titre et son texte | 1,4 | 26,9 | 7,1 |
| Écart photo / titre dans une carte G03 | 2,0 | 38,4 | 10,2 |
| Écart photo / titre dans une carte G04 | 1,6 | 30,7 | 8,1 |
| Largeur du logo | 12 | 230 | 61 |
| Largeur colonne de gauche / colonnes de droite (G03, G05, G06, G07, G08) | 1 part / 2,2 parts | – | – |
| G04 : carte titre / chaque carte photo | 1,25 part / 1 part | – | – |
| Hauteur des photos G03 | 27 | 518 | 137 |
| Hauteur des photos G03 à 4 cartes | 24 | 461 | 122 |
| Hauteur de la photo G02 | 27 | 518 | 137 |
| Photo G05 : format | 16:10, 2,4 u au-dessus | – | – |
| Photo G03 réalisations : format | 598:747 (≈ 4:5) | – | – |
| Téléphone de couverture G01 : largeur | 15 | 288 | 76 |
| Téléphone G01 : décalage depuis la droite / dépasse en bas de | 4 / 7 | 77 / 134 | 20 / 36 |
| Téléphone G03 variante C : largeur | 11 | 211 | 56 |
| Téléphone profil G06 / Reel G06 : largeur | 19 / 17 | 365 / 326 | 97 / 86 |
| Navigateur G07 : largeur | 58 | 1114 | 295 |

### 11.2 Tailles de texte (PDF)

| Texte | Classe | u | px (1920) | mm | Interligne |
|---|---|---|---|---|---|
| Grand titre | `h1`, `h2` | 4,6 | 88,3 | 23,4 | 0,98 |
| Grand titre réduit | `h2 class="sm"` | 3,5 | 67,2 | 17,8 | 1,02 |
| Grand titre G04 | `.side5 h2` | 3,4 | 65,3 | 17,3 | 0,98 |
| Promesse de couverture | `.cover-big` | 4,1 | 78,7 | 20,8 | 1,0 |
| Détail de couverture | `.cover-sub` | 3,1 | 59,5 | 15,7 | 1,08 |
| Phrase | `p.s` | 2,1 | 40,3 | 10,7 | 1,08 |
| Titre de carte G03 / ligne G05 | `.trio .s`, `.t` | 1,85 | 35,5 | 9,4 | 1,05 à 1,08 |
| Titre de carte G04 | `.pic .s` | 1,6 | 30,7 | 8,1 | 1,08 |
| Points du résumé G08 | `.sum .s` | 2,8 | 53,8 | 14,2 | 1,08 |
| Prix G08 | `.price` | 5,4 | 103,7 | 27,4 | 1,0 |
| Texte courant | `p.x`, `.d`, `.contact` | 1,2 | 23,0 | 6,1 | 1,45 (contact 1,6) |
| Texte courant G04 | `.pic .x` | 1,1 | 21,1 | 5,6 | 1,4 |
| Étiquette (majuscules, entourée) | `.label` | 0,95 | 18,2 | 4,8 | – |
| Numéro de ligne G05 | `.n` | 0,95 | 18,2 | 4,8 | – |

Espacement des lettres : titres −0,035 em, phrases −0,03 em, étiquettes +0,08 em.

### 11.3 Instagram (images 1080 × 1350 px)

| Élément | px |
|---|---|
| Marge blanche autour de la carte | 40 |
| Arrondi de la carte | 40 |
| Marge intérieure de la carte | 76 (cartes de série : 65) |
| Grand titre | 113 |
| Promesse de couverture | 103 |
| Détail de couverture | 80 |
| Phrase / titre de carte | 65 / 60 |
| Texte courant | 44 |
| Étiquette | 32 |

---

## 12. CHECKLIST FINALE (coche chaque ligne avant de livrer)

- [ ] `construire.py` affiche `OK` et AUCUN avertissement d'image grise.
- [ ] `verifier.js` affiche `AUCUN PROBLÈME.`
- [ ] `exporter.js` affiche `AUCUN PROBLÈME.`
- [ ] J'ai ouvert chaque `controle/diapo-XX.png` : aucun visage coupé, aucune photo floue.
- [ ] La 1re diapo est un G01, la dernière un G08.
- [ ] Aucun texte ne contient `'` (apostrophe droite) : uniquement `’`.
- [ ] Il y a `&nbsp;` avant chaque `?`, `!`, `:`, `;`, `€`, `%`.
- [ ] Les grands titres finissent par un point, les titres de carte non.
- [ ] Le prix de G01 et celui de G08 sont identiques.
- [ ] L'étiquette de G01 et celle de G08 sont identiques.
- [ ] Aucun prix n'apparaît dans `export/instagram/` (ouvre la 2e image du 1er carrousel et le dernier carrousel).
- [ ] Chaque `<section>` a un `data-nom` différent.
- [ ] Je n'ai modifié aucun fichier dans `assets/` ni dans `outils/`.

---

## 13. EXEMPLE COMPLET

`exemples/offre-decouverte/source.html` est une proposition réelle, validée, de 9 diapos.
Elle utilise G01, G03 variante C, G04, G05 (numéros 06 à 10), G06, G07 avec logo, G07 sans logo, G03 variante A, G08.
En cas de doute sur la façon d'écrire quelque chose, regarde comment c'est écrit là et fais pareil.
