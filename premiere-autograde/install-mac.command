#!/bin/bash
# Installe le panneau Claude AutoGrade dans Premiere Pro (macOS).
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Library/Application Support/Adobe/CEP/extensions/claude-autograde"

# Autorise les extensions non signées (mode développeur CEP), pour toutes les versions récentes.
for v in 9 10 11 12 13; do
  defaults write "com.adobe.CSXS.$v" PlayerDebugMode 1
done

mkdir -p "$DEST"
rsync -a --delete --exclude tests --exclude 'install-*' --exclude '.DS_Store' "$SRC/" "$DEST/"

echo
echo "Claude AutoGrade est installé dans :"
echo "  $DEST"
echo
echo "Redémarre Premiere Pro, puis ouvre Fenêtre > Extensions > Claude AutoGrade."
read -r -p "Appuie sur Entrée pour fermer..."
