"""Génère les gabarits du kit, l'exemple Offre Découverte et le catalogue des emplacements."""
import re, os
K = '/home/user/claudecode/Kit_Propositions_Recitales/'

def svg(d): return '<svg viewBox="0 0 24 24">' + d + '</svg>'
SIDE = (svg('<path d="M12 20.5s-7.5-4.6-9.2-9.3C1.6 7.8 3.9 4.5 7.3 4.5c2 0 3.6 1.1 4.7 2.8 1.1-1.7 2.7-2.8 4.7-2.8 3.4 0 5.7 3.3 4.5 6.7-1.7 4.7-9.2 9.3-9.2 9.3z"/>')
        + svg('<path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20.5l1.6-5A8.5 8.5 0 1 1 21 11.5z"/>')
        + svg('<path d="M22 3L9.2 13.2"/><path d="M22 3l-6.5 18-3.3-7.8L3.5 9.7z"/>'))
TABS = ('<span>' + svg('<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>') + '</span>'
        + '<span>' + svg('<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M3 8.5h18M8 3l3 5.5M14 3l3 5.5"/><path d="M10 12v5l4.3-2.5z"/>') + '</span>'
        + '<span>' + svg('<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="12" cy="10" r="3"/><path d="M6.5 21c.8-3 3-4.6 5.5-4.6s4.7 1.6 5.5 4.6"/>') + '</span>')
RL = '<svg class="fx-rl" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm5 6v7l6-3.5z"/></svg>'
LOGO = '<div class="logo" role="img" aria-label="Studio Récitales"></div>'
P = 'style="object-position:50% 50%"'

def reel(img_kind, compte, legende, desc, width, extra_cls=''):
    return ('<figure class="fx fx-tel fx-reel%s" style="width:%s"><div class="fx-b"><div class="fx-in">'
            '<img alt="%s" src="{{img:@%s}}" %s><div class="fx-ui"><div class="fx-top">Reels</div>'
            '<div class="fx-side">%s</div><div class="fx-bot"><div class="fx-who"><div class="fx-av"></div>'
            '<div class="fx-t">%s</div></div><div class="fx-t fx-cap">%s</div></div></div></div></div></figure>'
            % (extra_cls, width, desc, img_kind, P, SIDE, compte, legende))

def card3(color, n, g, extra=''):
    return ('    <div class="card %s%s"><div class="vis"><img alt="[[%s_C%d_PHOTO_DESCRIPTION]]" src="{{img:@portrait}}" %s></div>'
            '<div class="stack"><p class="s">[[%s_C%d_TITRE]]</p><p class="x">[[%s_C%d_TEXTE]]</p></div></div>\n'
            % (color, extra, g, n, P, g, n, g, n))

G = {}
G['G01_couverture'] = '''<!-- =====================================================================
     G01 · COUVERTURE : question à gauche, promesse + téléphone à droite.
     Images : 1 photo VERTICALE (format 9:16) pour l'écran du téléphone.
     ===================================================================== -->
<section class="page c2" data-nom="accroche"><div class="in">
  <div class="card g between cover-l">
    ''' + LOGO + '''
    <div class="stack">
      <span class="label">[[G01_ETIQUETTE]]</span>
      <h1>[[G01_QUESTION]]</h1>
    </div>
  </div>
  <div class="card y cover-r">
    <div class="stack">
      <p class="cover-big">[[G01_PROMESSE]]</p>
      <p class="cover-sub" data-insta-texte="[[G01_DETAIL_INSTAGRAM]]">[[G01_DETAIL]] <span class="hl">[[G01_PRIX]]</span>.</p>
    </div>
    ''' + reel('vertical', '[[G01_COMPTE]]', '[[G01_LEGENDE]]', '[[G01_PHOTO_DESCRIPTION]]', '15cqw', ' cover-tel') + '''
  </div>
</div></section>
'''
G['G02_introduction'] = '''<!-- =====================================================================
     G02 · INTRODUCTION : deux cartes de texte, une photo en bas à droite.
     Images : 1 photo PAYSAGE (format 16:10 ou 3:2).
     ===================================================================== -->
<section class="page c2" data-nom="introduction"><div class="in">
  <div class="card g between">
    ''' + LOGO + '''
    <p class="s">[[G02_TEXTE_GAUCHE]]</p>
  </div>
  <div class="card y">
    <p class="s">[[G02_TEXTE_DROITE]]</p>
    <div class="intro-ph"><img alt="[[G02_PHOTO_DESCRIPTION]]" src="{{img:@paysage}}" ''' + P + '''></div>
  </div>
</div></section>
'''
G['G03_trois_cartes'] = '''<!-- =====================================================================
     G03 · TROIS CARTES PHOTO : une carte titre à gauche, 3 cartes photo + texte.
     Images : 3 photos PORTRAIT (format 4:5 ou 3:4).
     Variantes (réalisations, 4 cartes, téléphone) : voir INSTRUCTIONS_ANTIGRAVITY.md, partie G03.
     ===================================================================== -->
<section class="page side" data-nom="trois-cartes"><div class="in">
  <div class="card b between">
    <p class="s">[[G03_INTRO]]</p>
    <h2>[[G03_TITRE]]</h2>
  </div>
  <div class="trio">
''' + card3('g', 1, 'G03') + card3('y', 2, 'G03') + card3('b', 3, 'G03') + '''  </div>
</div></section>
'''
pics = ''
for i, c in enumerate(['g', 'y', 'b', 'g', 'y'], 1):
    pics += ('  <div class="card %s pic"><div class="vis"><img alt="[[G04_C%d_PHOTO_DESCRIPTION]]" src="{{img:@portrait}}" %s></div>'
             '<div class="stack"><p class="s">[[G04_C%d_TITRE]]</p><p class="x">[[G04_C%d_TEXTE]]</p></div></div>\n' % (c, i, P, i, i))
G['G04_cinq_cartes'] = '''<!-- =====================================================================
     G04 · CINQ CARTES PHOTO : une carte titre étroite à gauche, 5 cartes hautes.
     Images : 5 photos PORTRAIT (format 4:5, 3:4 ou plus haut). Visage au centre.
     ===================================================================== -->
<section class="page side5" data-nom="cinq-cartes"><div class="in">
  <div class="card b between lead">
    <p class="s">[[G04_INTRO]]</p>
    <h2>[[G04_TITRE]]</h2>
  </div>
''' + pics + '''</div></section>
'''
rows = ''
for i in range(1, 6):
    rows += ('    <div class="row"><span class="n">0%d</span><p class="t">[[G05_L%d_TITRE]]</p><p class="d">[[G05_L%d_TEXTE]]</p></div>\n' % (i, i, i))
G['G05_liste'] = '''<!-- =====================================================================
     G05 · LISTE NUMÉROTÉE : carte titre + photo à gauche, liste de 3 à 5 lignes à droite.
     Images : 1 photo PAYSAGE (format 16:10).
     Les numéros (01, 02...) s'écrivent directement dans <span class="n">.
     ===================================================================== -->
<section class="page side" data-nom="liste"><div class="in">
  <div class="card g">
    <span class="label">[[G05_ETIQUETTE]]</span>
    <div class="stack end">
      <h2>[[G05_TITRE]]</h2>
      <p class="x">[[G05_SOUS_TITRE]]</p>
    </div>
    <div class="side-ph"><img alt="[[G05_PHOTO_DESCRIPTION]]" src="{{img:@paysage}}" ''' + P + '''></div>
  </div>
  <div class="card y"><div class="list">
''' + rows + '''  </div></div>
</div></section>
'''
tiles = ''.join('<div class="fx-tile"><img alt="" src="{{img:@portrait|300}}" %s>%s</div>' % (P, RL) for _ in range(12))
G['G06_instagram'] = '''<!-- =====================================================================
     G06 · INSTAGRAM : texte à gauche, profil Instagram + Reel dans deux téléphones.
     Images : 12 petites photos PORTRAIT pour la grille du profil (on peut répéter les mêmes),
              1 photo VERTICALE (9:16) pour le Reel.
     ===================================================================== -->
<section class="page side" data-nom="instagram"><div class="in">
  <div class="card b between">
    <span class="label">[[G06_ETIQUETTE]]</span>
    <div class="stack">
      <h2 class="sm">[[G06_TITRE]]</h2>
      <p class="x">[[G06_TEXTE]]</p>
    </div>
  </div>
  <div class="card g"><div class="duo-tel">
    <figure class="fx fx-tel fx-profil" style="width:19cqw"><div class="fx-b"><div class="fx-in"><div class="fx-ig">
      <div class="fx-user"><div class="fx-t">[[G06_COMPTE]]</div></div>
      <div class="fx-row"><div class="fx-av"></div><div class="fx-stats"><div><div class="fx-t"><b>[[G06_PUBLICATIONS]]</b></div><span>publications</span></div><div><div class="fx-t"><b>[[G06_FOLLOWERS]]</b></div><span>followers</span></div><div><div class="fx-t"><b>[[G06_SUIVIS]]</b></div><span>suivi(e)s</span></div></div></div>
      <div class="fx-t fx-name">[[G06_NOM]]</div><div class="fx-t fx-bio">[[G06_BIO]]</div>
      <div class="fx-btns"><span>Suivre</span><span>Message</span></div>
      <div class="fx-tabs">''' + TABS + '''</div>
      <div class="fx-grid">''' + tiles + '''</div>
    </div></div></div></figure>
    ''' + reel('vertical', '[[G06_COMPTE]]', '[[G06_LEGENDE]]', '[[G06_PHOTO_DESCRIPTION]]', '17cqw') + '''
  </div></div>
</div></section>
'''
G['G07_capture_site'] = '''<!-- =====================================================================
     G07 · CAPTURE DE SITE : titre à gauche, page web dans une fenêtre de navigateur.
     Images : 1 CAPTURE D'ÉCRAN de site (format 16:10, le haut de la page est gardé).
     ===================================================================== -->
<section class="page side" data-nom="site"><div class="in">
  <div class="card g between">''' + LOGO + '''<h2>[[G07_TITRE]]</h2></div>
  <div class="card y center">
    <figure class="fx fx-nav" style="width:58cqw"><div class="fx-b"><div class="fx-hd"><i></i><i></i><i></i><div class="fx-t fx-url">[[G07_ADRESSE]]</div></div><div class="fx-in"><img alt="[[G07_PHOTO_DESCRIPTION]]" src="{{img:@capture}}" style="object-position:50% 0"></div></div></figure>
  </div>
</div></section>
'''
G['G08_resume_contact'] = '''<!-- =====================================================================
     G08 · RÉSUMÉ ET CONTACT : titre à gauche, 3 cartes (offre, prix, contact).
     Images : aucune.
     ===================================================================== -->
<section class="page side sum" data-nom="resume"><div class="in">
  <div class="card g between">''' + LOGO + '''<h2>[[G08_TITRE]]</h2></div>
  <div class="trio">
    <div class="card y"><span class="label">[[G08_ETIQUETTE]]</span><div class="stack end"><p class="s">[[G08_POINT_1]]</p><p class="x">[[G08_POINT_1_DETAIL]]</p></div></div>
    <div class="card b"><div class="stack end"><p class="s price" data-insta="masquer">[[G08_PRIX]]</p><p class="s">[[G08_POINT_2]]</p><p class="x">[[G08_POINT_2_DETAIL]]</p></div></div>
    <div class="card g"><div class="stack end"><p class="contact">[[G08_NOM]]<br><a href="tel:[[G08_TELEPHONE_LIEN]]">[[G08_TELEPHONE]]</a><br><a href="mailto:[[G08_EMAIL]]">[[G08_EMAIL]]</a><br><a href="https://[[G08_SITE]]/">[[G08_SITE]]</a></p><a class="btn" href="mailto:[[G08_EMAIL]]?subject=[[G08_SUJET_EMAIL]]">[[G08_BOUTON]]</a></div></div>
  </div>
</div></section>
'''
SQUELETTE = '''<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>[[TITRE_DU_DOCUMENT]]</title>
<!-- STYLES DU KIT -->
</head>
<body>

<!-- COLLER LES DIAPOS ICI, DANS L'ORDRE, LES UNES SOUS LES AUTRES -->

</body></html>
'''

os.makedirs(K + 'gabarits', exist_ok=True)
open(K + 'gabarits/G00_squelette.html', 'w', encoding='utf-8').write(SQUELETTE)
for name, html in G.items():
    open(K + 'gabarits/%s.html' % name, 'w', encoding='utf-8').write(html)


def strip_comment(h): return re.sub(r'<!-- =+.*?=+ -->\n', '', h, flags=re.S)

def fill(html, vals, imgs=None):
    for k, v in vals.items():
        html = html.replace('[[%s]]' % k, v)
    if imgs:
        for path, pos in imgs:
            html = re.sub(r'\{\{img:@[a-z]+(\|\d+)?\}\}" style="object-position:[^"]*"',
                          lambda m: '{{img:%s%s}}" style="object-position:%s"' % (path, m.group(1) or '', pos), html, count=1)
    left = re.findall(r'\[\[[^\]]+\]\]', html)
    assert not left, left
    return html

def page(title, body): return SQUELETTE.replace('[[TITRE_DU_DOCUMENT]]', title).replace(
    "<!-- COLLER LES DIAPOS ICI, DANS L'ORDRE, LES UNES SOUS LES AUTRES -->\n", body)

# ---------- valeurs de l'exemple Offre Découverte ----------
V = {
 'G01': dict(G01_ETIQUETTE='Offre Découverte', G01_QUESTION='Vous préparez une nouveauté, une promo ou une offre spéciale pour les fêtes&nbsp;?',
             G01_PROMESSE='On vous aide à la faire découvrir.', G01_DETAIL='10&nbsp;vidéos tournées chez vous en 2&nbsp;heures, pour',
             G01_PRIX='100&nbsp;€', G01_DETAIL_INSTAGRAM='10&nbsp;vidéos tournées chez vous en 2&nbsp;heures.',
             G01_COMPTE='votre_compte', G01_LEGENDE='Notre nouveauté pour les fêtes', G01_PHOTO_DESCRIPTION='Samuel Perraro dans son atelier'),
 'G03': dict(G03_INTRO='On vient à votre rencontre pendant deux heures pour présenter votre activité, ce que vous proposez, et le mettre en valeur.',
             G03_TITRE='Notre format.',
             G03_C1_TITRE='L’échange', G03_C1_TEXTE='Vous nous parlez de votre projet et de ce que vous préparez pour les fêtes.', G03_C1_PHOTO_DESCRIPTION='Interview filmée',
             G03_C2_TITRE='L’immersion', G03_C2_TEXTE='On vous filme en action, sans bloquer votre journée.', G03_C2_PHOTO_DESCRIPTION='Tournage dans l’atelier',
             G03_C3_TITRE='Les livrables', G03_C3_TEXTE='Dix vidéos de plus d’une minute, montées et sous-titrées, prêtes à publier.', G03_C3_PHOTO_DESCRIPTION='Vidéo sous-titrée'),
 'G04': dict(G04_INTRO='Cinq vidéos pour faire découvrir ce que vous préparez.', G04_TITRE='Pour les fêtes.',
             G04_C1_TITRE='Votre nouveauté', G04_C1_TEXTE='Ce que vous lancez pour les fêtes, présenté par vous.', G04_C1_PHOTO_DESCRIPTION='Mélissa Beynet prépare une toile',
             G04_C2_TITRE='Votre offre ou votre promo', G04_C2_TEXTE='Expliquée simplement, face caméra, pour qu’on la comprenne tout de suite.', G04_C2_PHOTO_DESCRIPTION='Mélissa Beynet face caméra',
             G04_C3_TITRE='Vos idées cadeaux', G04_C3_TEXTE='Un produit, une séance, un bon cadeau&nbsp;: ce qu’on peut offrir grâce à vous.', G04_C3_PHOTO_DESCRIPTION='Mélissa Beynet tient une de ses créations',
             G04_C4_TITRE='Les infos pratiques', G04_C4_TEXTE='Horaires, dates limites, comment commander ou réserver.', G04_C4_PHOTO_DESCRIPTION='Mélissa Beynet avec une cliente',
             G04_C5_TITRE='Votre message de fin d’année', G04_C5_TEXTE='Un merci à vos clients et ce qui les attend en janvier.', G04_C5_PHOTO_DESCRIPTION='Portrait de Mélissa Beynet'),
 'G05': dict(G05_ETIQUETTE='Cinq vidéos', G05_TITRE='Pour votre activité.', G05_SOUS_TITRE='Elles servent bien après les fêtes.', G05_PHOTO_DESCRIPTION='Les mains de Samuel Perraro',
             G05_L1_TITRE='Vous, derrière le projet', G05_L1_TEXTE='Votre déclic, votre parcours, ce qui vous motive. On préfère soutenir une vraie personne.',
             G05_L2_TITRE='Votre méthode, pas à pas', G05_L2_TEXTE='Vos gestes, vos outils. Le client voit comment ça se passe avant d’acheter.',
             G05_L3_TITRE='Ce qui vous rend différent', G05_L3_TEXTE='Le problème que vous réglez et le résultat. Votre argumentaire, prêt à envoyer.',
             G05_L4_TITRE='Les coulisses et la qualité', G05_L4_TEXTE='Les matières, les gestes, les finitions. La valeur de votre travail se voit.',
             G05_L5_TITRE='L’accueil, pour rassurer', G05_L5_TEXTE='Comment vous recevez vos clients. Pour ceux qui hésitent à pousser la porte.'),
 'G06': dict(G06_ETIQUETTE='Sur votre compte', G06_TITRE='Tout ce que vous préparez pour les fêtes, en vidéo.',
             G06_TEXTE='Votre offre et votre activité, visibles dès qu’on ouvre votre profil.', G06_COMPTE='votre_compte',
             G06_PUBLICATIONS='128', G06_FOLLOWERS='1 240', G06_SUIVIS='312', G06_NOM='Votre activité', G06_BIO='Nos nouveautés et nos offres pour les fêtes',
             G06_LEGENDE='Notre offre des fêtes, expliquée en une minute', G06_PHOTO_DESCRIPTION='Caroline Dinet au travail'),
 'G07a': dict(G07_TITRE='Qui nous sommes.', G07_ADRESSE='studiorecitales.fr', G07_PHOTO_DESCRIPTION='Page d’accueil du site Studio Récitales'),
 'G07b': dict(G07_TITRE='Nos services.', G07_ADRESSE='studiorecitales.fr/services', G07_PHOTO_DESCRIPTION='Page services du site Studio Récitales'),
 'G03r': dict(G03_TITRE='Nos réalisations.',
              G03_C1_TITRE='Samuel Perraro', G03_C1_TEXTE='Céramiste', G03_C1_PHOTO_DESCRIPTION='Samuel Perraro',
              G03_C2_TITRE='Atelier Symbiose', G03_C2_TEXTE='Mélissa Beynet<br>Tufting, Marseille', G03_C2_PHOTO_DESCRIPTION='Atelier Symbiose',
              G03_C3_TITRE='Caroline Dinet', G03_C3_TEXTE='Lambesc<br>Restauration d’œuvres', G03_C3_PHOTO_DESCRIPTION='Caroline Dinet'),
 'G08': dict(G08_TITRE='L’offre en résumé.', G08_ETIQUETTE='Offre Découverte', G08_POINT_1='Dix vidéos.', G08_POINT_1_DETAIL='Cinq pour les fêtes, cinq pour votre activité.',
             G08_PRIX='100&nbsp;€', G08_POINT_2='Deux heures chez vous.', G08_POINT_2_DETAIL='Déplacement inclus.',
             G08_NOM='Studio Récitales', G08_TELEPHONE='06 75 14 68 71', G08_TELEPHONE_LIEN='+33675146871', G08_EMAIL='hello@studiorecitales.fr',
             G08_SITE='studiorecitales.fr', G08_SUJET_EMAIL='Offre%20D%C3%A9couverte%20f%C3%AAtes', G08_BOUTON='Réserver mon tournage'),
 'G02': dict(G02_TEXTE_GAUCHE='Actuellement je chemine dans toute la région pour faire des portraits de gens qui ont leur activité sur notre territoire régional.',
             G02_TEXTE_DROITE='J’aimerais vous proposer de faire les portraits de dix activités que vous accompagnez. Je me déplacerai à mes frais pour aller à leur rencontre et mettre en valeur leur activité.',
             G02_PHOTO_DESCRIPTION='Samuel Perraro, céramiste'),
}
I = 'images/'
MOCK = ('<div class="vis mock"><figure class="fx fx-tel fx-reel" style="width:11cqw"><div class="fx-b"><div class="fx-in">'
        '<img alt="[[G03_C3_PHOTO_DESCRIPTION]]" src="{{img:@vertical}}" ' + P + '></div></div></figure></div>')

def g03_mock(h):  # variante C : téléphone dans la 3e carte
    i = h.index('<div class="card b"><div class="vis">')
    j = h.index('</div>', h.index('<img', i)) + 6
    return h[:i] + '<div class="card b">' + MOCK + h[j:]

def g03_real(h):  # variante A : réalisations
    h = h.replace('<div class="card g"><div class="vis">', '<div class="card g real"><div class="vis">')
    h = h.replace('<div class="card y"><div class="vis">', '<div class="card y real"><div class="vis">')
    h = h.replace('<div class="card b"><div class="vis">', '<div class="card b real"><div class="vis">')
    return h.replace('<p class="s">[[G03_INTRO]]</p>', '<span></span>')

def g07_sans_logo(h, c1, c2):
    h = h.replace('<div class="card g between">' + LOGO, '<div class="card %s between"><span></span>' % c1)
    return h.replace('<div class="card y center">', '<div class="card %s center">' % c2)

s = lambda k: strip_comment(G[k])
offre = [
 fill(s('G01_couverture'), V['G01'], [(I + 'reel-samuel.jpg', '50% 50%')]),
 fill(g03_mock(s('G03_trois_cartes')).replace('data-nom="trois-cartes"', 'data-nom="notre-format"'), V['G03'],
      [(I + 'melissa-interview.jpg', '50% 50%'), (I + 'samuel-atelier.jpg', '40% 50%'), (I + 'reel-caroline-1.jpg', '50% 50%')]),
 fill(s('G04_cinq_cartes').replace('data-nom="cinq-cartes"', 'data-nom="pour-les-fetes"'), V['G04'],
      [(I + 'melissa-toile.jpg', '50% 50%'), (I + 'melissa-interview.jpg', '50% 50%'), (I + 'melissa-creation.jpg', '50% 60%'),
       (I + 'melissa-atelier-cliente.jpg', '42% 50%'), (I + 'melissa-portrait.jpg', '47% 40%')]),
 fill(s('G05_liste').replace('data-nom="liste"', 'data-nom="pour-votre-activite"')
      .replace('"n">01<', '"n">06<').replace('"n">02<', '"n">07<').replace('"n">03<', '"n">08<').replace('"n">04<', '"n">09<').replace('"n">05<', '"n">10<'),
      V['G05'], [(I + 'samuel-mains.jpg', '50% 50%')]),
 fill(s('G06_instagram').replace('data-nom="instagram"', 'data-nom="sur-votre-compte"'), V['G06'],
      [(I + 'tuile-%02d.jpg' % i, '50% 50%') for i in range(1, 13)] + [(I + 'reel-caroline-2.jpg', '50% 50%')]),
 fill(s('G07_capture_site').replace('data-nom="site"', 'data-nom="qui-nous-sommes"'), V['G07a'], [(I + 'capture-accueil.jpg', '50% 0')]),
 fill(g07_sans_logo(s('G07_capture_site'), 'y', 'b').replace('data-nom="site"', 'data-nom="nos-services"'), V['G07b'], [(I + 'capture-services.jpg', '50% 0')]),
 fill(g03_real(s('G03_trois_cartes')).replace('data-nom="trois-cartes"', 'data-nom="nos-realisations"'), V['G03r'],
      [(I + 'realisation-samuel.jpg', '50% 50%'), (I + 'realisation-melissa.jpg', '50% 50%'), (I + 'realisation-caroline.jpg', '50% 50%')]),
 fill(s('G08_resume_contact').replace('data-nom="resume"', 'data-nom="l-offre-en-resume"'), V['G08']),
]
for i, h in enumerate(offre):
    offre[i] = '<!-- Diapo %d -->\n' % (i + 1) + h
open(K + 'exemples/offre-decouverte/source.html', 'w', encoding='utf-8').write(page('Offre Découverte fêtes', '\n'.join(offre)))

# ---------- catalogue : chaque gabarit avec le NOM de ses emplacements écrit dedans ----------
def names(h):
    return re.sub(r'\[\[([^\]]+)\]\]', lambda m: m.group(1).replace('_', ' '), h)
cat = []
for k in G:
    cat.append(names(s(k)).replace('data-nom="', 'data-nom="%s-' % k[:3]))
os.makedirs(K + 'exemples/catalogue-emplacements', exist_ok=True)
open(K + 'exemples/catalogue-emplacements/source.html', 'w', encoding='utf-8').write(page('Catalogue des emplacements', '\n'.join(cat)))

# ---------- variantes en exemple (G02, G03 à 4 cartes) ----------
g02 = fill(s('G02_introduction'), V['G02'], [(I + 'samuel-affiche.jpg', '50% 45%')])
g03q = s('G03_trois_cartes').replace('<div class="trio">', '<div class="trio quad">').replace(
    '  </div>\n</div></section>', card3('g', 4, 'G03') + '  </div>\n</div></section>')
q = dict(V['G03r']); q.update(G03_TITRE='Quatre portraits.', G03_INTRO='La même mise en page, avec quatre cartes.',
                         G03_C4_TITRE='Mélissa Beynet', G03_C4_TEXTE='Atelier Symbiose<br>Marseille', G03_C4_PHOTO_DESCRIPTION='Mélissa Beynet')
g03q = fill(g03q, q, [(I + 'realisation-samuel.jpg', '50% 50%'), (I + 'realisation-melissa.jpg', '50% 50%'),
                      (I + 'realisation-caroline.jpg', '50% 50%'), (I + 'melissa-creation.jpg', '50% 55%')])
os.makedirs(K + 'exemples/variantes', exist_ok=True)
open(K + 'exemples/variantes/source.html', 'w', encoding='utf-8').write(
    page('Variantes', (g02 + '\n' + g03q).replace('{{img:images/', '{{img:../offre-decouverte/images/')))
print('ok', list(G))
