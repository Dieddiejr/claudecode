#!/usr/bin/env python3
"""
construire.py : transforme une source de proposition en un fichier HTML autonome.

    python3 outils/construire.py projets/MON-PROJET/source.html projets/MON-PROJET/proposition.html

Ce que fait le script, dans l'ordre :
  1. Remplace le commentaire <!-- STYLES DU KIT --> par les polices et recitales.css
     (polices et logo inclus directement dans le fichier).
  2. Remplace chaque {{img:CHEMIN}} par l'image, réduite à 1600 px de large au maximum.
     CHEMIN est relatif au fichier source (ex. {{img:images/portrait-melissa.jpg}}).
     CHEMIN qui commence par @ = image d'exemple grise du kit (@portrait, @paysage,
     @vertical, @capture, @carre). Le script avertit s'il en reste.
     Pour une autre largeur maximale : {{img:images/photo.jpg|800}}.
  3. Refuse de construire s'il reste un emplacement [[...]] non remplacé.

Le fichier produit ne dépend de rien : on peut l'envoyer tel quel au client.
Besoin : Python 3 et Pillow (pip install Pillow).
"""
import base64, io, os, re, sys

try:
    from PIL import Image
except ImportError:
    sys.exit("ERREUR : il manque Pillow. Installe-le avec : pip install Pillow")

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(KIT, 'assets')
EXEMPLES = {'portrait': 'portrait.jpg', 'paysage': 'paysage.jpg', 'vertical': 'vertical.jpg',
            'capture': 'capture.jpg', 'carre': 'carre.jpg'}
MIME = {'.woff2': 'font/woff2', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}


def data_uri(path, max_w=1600):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.woff2':
        return 'data:font/woff2;base64,' + base64.b64encode(open(path, 'rb').read()).decode()
    im = Image.open(path)
    has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if has_alpha:
        im.convert('RGBA').save(buf, 'PNG', optimize=True)
        mime = 'image/png'
    else:
        im.convert('RGB').save(buf, 'JPEG', quality=84, optimize=True, progressive=True)
        mime = 'image/jpeg'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(buf.getvalue()).decode())


def css_inline(css_path):
    css = open(css_path, encoding='utf-8').read()
    base = os.path.dirname(css_path)
    def rep(m):
        p = os.path.normpath(os.path.join(base, m.group(2)))
        return "url('%s')" % data_uri(p)
    return re.sub(r"url\((['\"]?)([^'\")]+\.(?:woff2|png|jpg))\1\)", rep, css)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    base = os.path.dirname(os.path.abspath(src))
    html = open(src, encoding='utf-8').read()

    oublis = sorted(set(re.findall(r'\[\[[^\]]+\]\]', html)))
    if oublis:
        print('ERREUR : ces emplacements n\'ont pas été remplacés :')
        for o in oublis:
            print('   ', o)
        sys.exit(1)

    if '<!-- STYLES DU KIT -->' not in html:
        sys.exit('ERREUR : le commentaire <!-- STYLES DU KIT --> manque dans le <head>. Recopie le squelette.')
    styles = '<style>\n' + css_inline(os.path.join(ASSETS, 'css', 'polices.css')) + '\n' + \
             css_inline(os.path.join(ASSETS, 'css', 'recitales.css')) + '\n</style>'
    html = html.replace('<!-- STYLES DU KIT -->', styles)

    exemples, manquantes = [], []
    def rep_img(m):
        spec = m.group(1).strip()
        chemin, _, largeur = spec.partition('|')
        max_w = int(largeur) if largeur.strip().isdigit() else 1600
        if chemin.startswith('@'):
            nom = EXEMPLES.get(chemin[1:])
            if not nom:
                manquantes.append(chemin)
                return ''
            exemples.append(chemin)
            p = os.path.join(ASSETS, 'placeholders', nom)
        else:
            p = os.path.normpath(os.path.join(base, chemin))
        if not os.path.isfile(p):
            manquantes.append(chemin)
            return ''
        return data_uri(p, max_w)
    html = re.sub(r'\{\{img:([^}]+)\}\}', rep_img, html)

    if manquantes:
        print('ERREUR : images introuvables (vérifie le nom et le dossier) :')
        for m in manquantes:
            print('   ', m)
        sys.exit(1)
    if '{{' in html:
        sys.exit('ERREUR : il reste des {{...}} mal écrits : ' + ', '.join(set(re.findall(r'\{\{[^}]*\}\}', html))))

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(html)
    print('OK : %s (%d Ko)' % (out, len(html) // 1024))
    if exemples:
        print('ATTENTION : %d image(s) d\'exemple grise(s) encore présente(s) : %s' % (len(exemples), ', '.join(sorted(set(exemples)))))
        print('            Remplace-les par de vraies photos avant d\'envoyer le document.')


if __name__ == '__main__':
    main()
