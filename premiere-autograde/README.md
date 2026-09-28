# Claude AutoGrade pour Premiere Pro

Panneau Premiere Pro qui fait l'étalonnage de base à ta place : il exporte une image de chaque plan, la fait analyser par Claude, puis règle l'effet **Lumetri Color** (section Correction de base). Tu vois un aperçu avant/après et une explication de chaque réglage, pour apprendre en même temps.

## Ce qu'il te faut

- Adobe Premiere Pro 2021 (v15) ou plus récent, sur Mac ou Windows
- Une clé API Anthropic : crée-la sur [console.anthropic.com](https://console.anthropic.com), dans **API Keys**. L'utilisation est payante, à l'usage. Compte quelques centimes par plan analysé (modèle `claude-opus-5-5`).

## Installation

1. Télécharge ce dossier `premiere-autograde` sur ton ordinateur.
2. Ferme Premiere Pro.
3. Lance le script d'installation :
   - **Mac** : clic droit sur `install-mac.command` > **Ouvrir**. La première fois, macOS demande une confirmation.
   - **Windows** : double-clic sur `install-windows.bat`.
4. Rouvre Premiere Pro, puis **Fenêtre > Extensions > Claude AutoGrade**.
5. Clique sur **Clé API**, colle ta clé et clique sur **Enregistrer**. La clé reste sur ton ordinateur.

Le script active le « mode développeur » des extensions Adobe (`PlayerDebugMode`), nécessaire pour les extensions qui ne sont pas publiées sur le marketplace d'Adobe.

## Utilisation

1. Dans la timeline, sélectionne un ou plusieurs plans. Sans sélection, le panneau prend le plan sous la tête de lecture.
2. Choisis un **style** : Naturel, Cinéma doux, Chaud, Froid, Documentaire ou Vif. Tu peux ajouter des précisions, par exemple « interview en intérieur, garder le ciel bleu ».
3. Clique sur **Analyser les plans** et regarde l'aperçu **Avant / Après**.
4. Ajuste l'**intensité** si c'est trop fort ou trop faible.
5. Clique sur **Appliquer dans Lumetri**, ou sur **Appliquer à tous** si tu as analysé plusieurs plans.

Les curseurs sont ensuite modifiables à la main dans le panneau Couleur Lumetri, comme d'habitude. **Remettre à zéro** remet ces curseurs au neutre.

### Bon à savoir

- **Relancer l'analyse remet d'abord les curseurs de la Correction de base de Lumetri au neutre**, pour que Claude analyse l'image d'origine. Tes éventuelles retouches manuelles de ces curseurs sont donc écrasées. Les courbes, roues et LUT ne sont pas touchées.
- **Rushs en log** (S-Log, V-Log, C-Log…) : applique d'abord la LUT de conversion de ta caméra (Lumetri > Correction de base > LUT d'entrée), puis lance l'analyse. Le panneau t'avertit s'il détecte une image log.
- L'image analysée est celle de la séquence au milieu du plan, y compris les titres ou calques placés au-dessus.
- **Solution de secours** : si le panneau n'arrive pas à régler certains curseurs (il le signale), clique sur **Exporter en LUT .cube**. Le fichier est enregistré sur le Bureau, dans `Claude AutoGrade`. Dans Lumetri, va dans **Créatif > Look > Parcourir…** et choisis ce fichier.
- L'aperçu du panneau est une approximation. Le rendu qui compte est celui de Premiere.

## En cas de problème

| Problème | Solution |
|---|---|
| Le panneau n'apparaît pas dans Fenêtre > Extensions | Relance le script d'installation, puis redémarre complètement Premiere. |
| « Clé API refusée » | Vérifie ta clé dans **Clé API** et le crédit de ton compte sur console.anthropic.com. |
| « Premiere n'a pas exporté l'image du plan » | Vérifie qu'une séquence est ouverte et active dans la timeline, puis réessaie. |
| « Impossible d'ajouter Lumetri Color automatiquement » | Glisse toi-même l'effet Lumetri Color sur le plan, puis clique à nouveau sur **Appliquer**. |
| « Réglages non trouvés dans Lumetri » | Utilise **Exporter en LUT .cube** et envoie-moi la liste affichée pour que j'ajoute ta langue ou ta version. |

## Pour les curieux (technique)

- Panneau CEP : HTML/JS dans `index.html` et `js/main.js`, script Premiere (ExtendScript) dans `jsx/host.jsx`.
- `js/grade-core.js` contient les consignes envoyées à Claude, le schéma de réponse (sortie JSON structurée), les mesures type scopes, l'aperçu et la génération de LUT.
- `js/vendor/anthropic-sdk.js` est le SDK officiel `@anthropic-ai/sdk` (v0.129.0) empaqueté pour le navigateur avec esbuild. Licence dans `anthropic-sdk.LICENSE`.
- Tests : `node --test tests/*.test.js`. Premiere est simulé : ces tests ne remplacent pas un essai dans le vrai logiciel.
- Adobe remplace progressivement CEP par UXP. Les panneaux CEP fonctionnent encore dans Premiere Pro, mais une version UXP sera nécessaire le jour où Adobe coupera CEP.
