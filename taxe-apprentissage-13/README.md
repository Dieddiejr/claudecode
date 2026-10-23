# Taxe d'apprentissage : bénéficiaires non publics des Bouches-du-Rhône

Cartographie des associations, fondations et établissements privés du 13 qui perçoivent ou sollicitent le solde (13 %) de la taxe d'apprentissage via SOLTéA, campagne 2026.

| Fichier | Contenu |
|---|---|
| `organismes_ta_13.csv` | Données sources (une ligne par organisme, séparateur `;`) |
| `organismes_ta_13.xlsx` | Registre, synthèse par catégorie, organismes exclus, méthode |
| `carte_ta_13.html` | Carte et registre interactifs (généré) |
| `build.py` | Régénère l'Excel, le JSON et la carte à partir du CSV |
| `filtrer_liste_officielle.py` | Filtre la liste officielle PACA : ne garde que les organismes non publics du 13 |

## Fiabilité

- **A** : l'organisme affiche lui-même sa collecte TA ou son habilitation SOLTéA (source citée).
- **B** : statut éligible au titre de l'article L6241-5 du Code du travail ; inscription SOLTéA 2026 non vérifiée.
- **C** : éligibilité ou statut incertain, à confirmer.

## Limite

La liste préfectorale PACA 2026 (arrêté du 26/05/2026, liste complémentaire au 24/07/2026) et la plateforme SOLTéA n'étaient pas accessibles depuis l'environnement de travail. Le recensement est donc reconstitué à partir des pages publiques des organismes et d'annuaires. Pour une liste exhaustive :

```bash
python3 filtrer_liste_officielle.py liste_prefectorale_PACA_2026.xlsx liste_regionale_SPRO_2026.xlsx
```

Le script repère les colonnes UAI, code postal, département et statut, et écrit `liste_officielle_13_non_publics.xlsx`.
