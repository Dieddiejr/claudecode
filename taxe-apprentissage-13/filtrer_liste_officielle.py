"""Filtre la liste officielle PACA (XLSX/CSV préfecture ou export SOLTéA) :
ne garde que les organismes NON PUBLICS situés dans les Bouches-du-Rhône.

Usage : python3 filtrer_liste_officielle.py liste_PACA_2026.xlsx [autre_liste.xlsx ...]
Sortie : liste_officielle_13_non_publics.xlsx

Les intitulés de colonnes varient d'une année à l'autre : le script les repère
par mots-clés (UAI, SIRET, code postal / commune / département, statut / secteur).
"""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def trouver(cols, *mots):
    for c in cols:
        if any(m in norm(c) for m in mots):
            return c
    return None


def charger(path):
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return {p.name: pd.read_csv(p, sep=None, engine="python", dtype=str)}
    feuilles = pd.read_excel(p, sheet_name=None, dtype=str, header=None)
    out = {}
    for nom, brut in feuilles.items():
        # La ligne d'en-tête n'est pas toujours la première : on prend la première
        # ligne qui contient « UAI » ou « SIRET ».
        idx = next((i for i, row in brut.iterrows()
                    if any(k in norm(v) for v in row.values for k in ("uai", "siret"))), None)
        if idx is None:
            continue
        df = brut.iloc[idx + 1:].copy()
        df.columns = [str(c) for c in brut.iloc[idx]]
        out[f"{p.name} / {nom}"] = df.dropna(how="all")
    return out


def est_13(row, c_cp, c_dep, c_uai):
    if c_dep and norm(row.get(c_dep, "")).startswith(("13", "bouches")):
        return True
    if c_cp and str(row.get(c_cp, "")).strip().startswith("13"):
        return True
    # À défaut, l'UAI d'un établissement du 13 commence par 013.
    return bool(c_uai) and str(row.get(c_uai, "")).strip().startswith("013")


def est_public(row, c_statut, c_nom):
    statut = norm(row.get(c_statut, "")) if c_statut else ""
    if statut:
        if "prive" in statut:
            return False
        if "public" in statut or "consulaire" in statut:
            return True
    nom = norm(row.get(c_nom, "")) if c_nom else ""
    publics = ("universite", "lycee public", "college public", "cci ", "chambre de commerce",
               "chambre de metiers", "chambre d'agriculture", "rectorat", "greta", "epide", "cnam")
    return any(p in nom for p in publics)


def main(paths):
    lignes = []
    for path in paths:
        for origine, df in charger(path).items():
            cols = list(df.columns)
            c_uai = trouver(cols, "uai")
            c_cp = trouver(cols, "code postal", "cp")
            c_dep = trouver(cols, "departement", "dept")
            c_statut = trouver(cols, "statut", "secteur", "public/prive", "nature")
            c_nom = trouver(cols, "denomination", "raison sociale", "nom", "etablissement", "organisme")
            for _, row in df.iterrows():
                row = row.to_dict()
                if est_13(row, c_cp, c_dep, c_uai) and not est_public(row, c_statut, c_nom):
                    row["_fichier_source"] = origine
                    lignes.append(row)
    if not lignes:
        sys.exit("Aucune ligne retenue : vérifier le fichier et les intitulés de colonnes.")
    res = pd.DataFrame(lignes).drop_duplicates()
    sortie = Path("liste_officielle_13_non_publics.xlsx")
    res.to_excel(sortie, index=False)
    print(f"{len(res)} lignes retenues -> {sortie}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
