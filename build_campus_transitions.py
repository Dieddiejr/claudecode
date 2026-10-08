# Génère « Radio Campus Transitions - proposition Studio Récitales » (HTML) à partir du gabarit thecamp (CSS + photos).
# Adapté de build_decks.py : les photos viennent du gabarit lui-même (le dossier d'origine n'est pas disponible)
# et le hero « Transitions+ » est rendu avec Chromium headless (à la place de SNAP).
# usage : python3 build_campus_transitions.py "<gabarit thecamp>.html" ["<sortie>.html" ["<sortie>.pdf"]]
#   (le PDF est facultatif : 12 pages 16:9, ~4 Mo, prêt à être joint à un e-mail)
import os,io,re,sys,base64,hashlib,subprocess,tempfile
from PIL import Image,ImageEnhance

TPL=sys.argv[1] if len(sys.argv)>1 else 'Radio thecamp - proposition Studio Récitales.html'
OUT=sys.argv[2] if len(sys.argv)>2 else 'Radio Campus Transitions - proposition Studio Récitales.html'
PDF=sys.argv[3] if len(sys.argv)>3 else None
CHROME=os.environ.get('CHROME','/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell')  # headless_shell : pas de barre de fenêtre, le viewport fait bien 1000×564

# ---------- photos : seules celles sans marque visible (thecamp, WEF…) sont gardées ----------
tpl=open(TPL,encoding='utf-8').read()
RAW={}
for m in re.finditer(r'data:image/jpeg;base64,([A-Za-z0-9+/=]+)',tpl):
    b=base64.b64decode(m.group(1)); RAW[hashlib.md5(b).hexdigest()[:8]]=b
KEYS=dict(A='192add8f',  # plateau d'interview (fond brique, lumières)
          B='522ba56a',  # conférence, public assis, orateur à l'écran
          C='7e5404e2',  # échange en cercle, fauteuils blancs
          D='1ad0f531',  # deux personnes à une table : coaching
          E='ca2f8335',  # micro flou
          F='adb51020')  # amphi plein, orateur de dos
POOL={k:Image.open(io.BytesIO(RAW[h])).convert('RGB') for k,h in KEYS.items()}

# ---------- utilitaires ----------
def uri(b,mime='image/jpeg'): return f'data:{mime};base64,'+base64.b64encode(b).decode()
def photo(k,w,ar,cx=.5,cy=.5,z=1.0,q=82,fx=None):
    """Recadre la photo k au ratio ar (largeur/hauteur) : centre (cx,cy) en fraction de l'image, z = part de la zone maximale.
    fx='gray' (noir et blanc) ou 'dark' (assombri) : l'effet est cuit dans l'image, pas en CSS, pour un PDF léger."""
    im=POOL[k]; W,H=im.size
    if W/H>ar: bh=H; bw=H*ar
    else: bw=W; bh=W/ar
    bw*=z; bh*=z
    l=min(max(cx*W-bw/2,0),W-bw); t=min(max(cy*H-bh/2,0),H-bh)
    w=min(w,round(bw)); c=im.crop((round(l),round(t),round(l+bw),round(t+bh))).resize((w,round(w/ar)),Image.LANCZOS)
    if fx=='gray': c=ImageEnhance.Contrast(c.convert('L')).enhance(1.05)
    elif fx=='dark': c=ImageEnhance.Brightness(c).enhance(.72)
    b=io.BytesIO(); c.save(b,'JPEG',quality=q,optimize=True); return uri(b.getvalue())
NOBREAK=['Fos-Berre','Château-Gombert','enseignants-chercheurs','enseignant-chercheur','rendez-vous']  # jamais coupés en fin de ligne
def typo(s):
    s=s.replace(' ?','&nbsp;?').replace(' !','&nbsp;!').replace(' :','&nbsp;:').replace('« ','«&nbsp;').replace(' »','&nbsp;»').replace(' %','&nbsp;%').replace('&amp;nbsp;','&nbsp;')
    for w in NOBREAK: s=s.replace(w,f'<span style="white-space:nowrap">{w}</span>')
    return s
T=typo

# ---------- hero « Transitions+ » ----------
def hero(c):
    thumbs=''.join(f'<div class="t" style="background-image:url({photo(k,620,.8,cx,cy,z,88)})"></div>' for k,cx,cy,z in c['thumbs'])
    html=f'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500&display=swap" rel="stylesheet">
<style>
:root{{--cream:{c['bg']};--ink:{c['ink']};--accent:{c['accent']};--font:"Inter Tight","Helvetica Neue",Arial,sans-serif}}
*{{box-sizing:border-box}}
html,body{{margin:0;width:1000px;height:563.5px;overflow:hidden;background:var(--cream);font-family:var(--font);color:var(--ink);-webkit-font-smoothing:antialiased}}
.hero{{padding:16.4px 0 0}}
.wordmark{{font-weight:500;font-size:{c.get('wmsize',160)}px;line-height:.95;letter-spacing:-.045em;margin:0;display:flex;align-items:baseline;justify-content:center;gap:.04em;white-space:nowrap}}
.wordmark .plus{{display:inline-block;width:.62em;height:.62em;position:relative;align-self:center}}
.wordmark .plus::before,.wordmark .plus::after{{content:"";position:absolute;background:var(--accent);border-radius:.05em}}
.wordmark .plus::before{{left:42%;width:16%;top:0;bottom:0}}
.wordmark .plus::after{{top:42%;height:16%;left:0;right:0}}
.thumbs{{display:grid;grid-template-columns:repeat(4,1fr);gap:13.5px;margin:{c.get('thumbtop',45)}px auto 0;width:943px;align-items:start}}
.thumbs .t{{aspect-ratio:4/5;border-radius:14px;background-size:cover;background-position:center;box-shadow:0 8px 24px rgba(0,0,0,.12)}}
.thumbs .t:nth-child(2n){{margin-top:37.5px}}
</style></head><body><div class="hero"><h1 class="wordmark">{c['wm']}<span class="plus"></span></h1><div class="thumbs">{thumbs}</div></div></body></html>'''
    with tempfile.TemporaryDirectory() as d:
        hp=os.path.join(d,'hero.html'); pp=os.path.join(d,'hero.png')
        open(hp,'w',encoding='utf8').write(html)
        subprocess.run([CHROME,'--no-sandbox','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=2',
                        '--window-size=1000,564','--virtual-time-budget=8000',f'--screenshot={pp}','file://'+hp],check=True,capture_output=True)
        im=Image.open(pp).convert('RGB').crop((0,0,2000,1127))
        if os.environ.get('HERO_PREVIEW'): im.save(os.environ['HERO_PREVIEW'],quality=90)
    b=io.BytesIO(); im.save(b,'JPEG',quality=90,optimize=True); return b.getvalue()

# ---------- textes communs (valeurs par défaut du gabarit) ----------
D_S10_Y="Le temps d’une journée portes ouvertes, un plateau radio pop-up s’installe sur le campus : {who} au micro. Un pilote concret, montré plutôt que promis."
D_S11_2="Le temps d’une journée portes ouvertes, puis un jour par semaine : une conférence, un séminaire, une rencontre."
D_S11_3="Montage et diffusion : nous nous occupons du reste."

# ---------- le Campus Transitions ----------
C=dict(slug='campus-transitions',file='Radio Campus Transitions',wm='Transitions',wmsize=140,thumbtop=60,
 logo='radio campus transitions',tile='CAMPUS TRANSITIONS',plat='Transitions+',
 cover='Et si on lançait une radio Campus Transitions ?',ink='#0F2F3F',accent='#1FA67A',bg='#F6F3EC',
 thumbs=[('A',.3,.5,.9),('E',.68,.62,.8),('C',.5,.45,.85),('F',.82,.68,.7)],
 cols=["Les conférences, les ateliers et les rencontres du campus, partout où ils se tiennent, en continu.",
       "Des ateliers pour apprendre à prendre la parole, vulgariser un sujet technique et convaincre.",
       "Aux industriels, aux étudiants, aux salariés en formation, aux chercheurs et aux collectivités.",
       "La voix des transitions industrielles dans le Sud : décarbonation, compétences et solutions."],
 t3="Et si les conférences ne s’arrêtaient plus à la porte de la salle ?",big3="Tout ce qui se dit au Campus Transitions, réécoutable.",
 y3="Industriels, chercheurs, élus, étudiants : ils prennent la parole lors des journées et des ateliers du campus. Avec une radio, chaque intervention serait enregistrée, diffusée en continu et rangée dans une bibliothèque sonore.",
 g3="Nous concevons pour vous une plateforme, « Transitions+ », pour retrouver toutes les conférences et interventions faites sur le campus.",
 t4="Et si chacun apprenait à expliquer la transition ?",
 p4="Des ateliers au micro et face caméra, pour les étudiants, les salariés en formation et l’équipe : vulgariser un sujet technique, partager un retour d’expérience, convaincre un décideur.",
 t5="Et si les industriels avaient enfin leur propre micro ?",h5="Made in Fos-Berre",
 p5="Industriels, salariés en formation, étudiants et chercheurs viennent raconter leurs projets de décarbonation, leurs réussites et leurs questions. Tout l’écosystème se raconte, et se fait connaître.",
 t6="Et si le Campus devenait aussi le média de la décarbonation ?",g6="Là où l’industrie du Sud parle de sa transition.",
 y6="La zone de Fos-Berre prépare près de 20&nbsp;milliards d’euros d’engagements industriels d’ici 2030 et environ 10&nbsp;000 emplois à créer ou à transformer : le territoire a des choses à dire. Votre radio serait l’endroit où elles se disent.",
 b6="S’exprimer, discuter, débattre.",
 t7="Et si les décideurs avaient rendez-vous au Campus Transitions ?",g7="Les Rencontres des Transitions",
 y7="La radio présente chaque semaine, là où le campus se tient, pour recevoir industriels, élus, chercheurs et porteurs de projets : leur actualité, leurs projets, leur regard sur l’avenir de l’industrie.",
 t8="Et si on suivait la décarbonation de près, chaque semaine ?",h8="Là où l’on apprend à décarboner l’industrie.",
 p8="La radio suivrait les avancées : procédés bas carbone, énergies, économie circulaire, nouveaux métiers, avec les enseignants-chercheurs, les industriels et les experts du campus.",
 t9="Et si le Campus devenait la voix de l’industrie de demain ?",y9="Transition",
 d9="Vos enseignants-chercheurs, vos industriels et vos étudiants partagent leurs réflexions sur la décarbonation et l’industrie de demain. Un rendez-vous que l’on écoute partout : en voiture le matin, à la pause, le soir.",
 ph9="Industrie<br>&amp; climat",g9="Compétences<br>de demain",
 t10="Et si la radio s’invitait au cœur de vos événements ?",
 y10="Le lancement du 1er octobre a réuni près de 300 personnes à Château-Gombert. Pour le prochain grand rendez-vous, un plateau radio pop-up s’installe sur place : une animation de plus pour le public.",
 jpo="une journée de rencontres du Campus",
 jpo_mid="Une table ronde sur la décarbonation de la zone de Fos-Berre, avec le micro tendu aux industriels, aux élus et aux étudiants.",
 s11_1="Sur le technopôle de Château-Gombert, dans une salle de cours ou chez un partenaire, pour une heure ou deux : une radio éphémère.",
 s11_2="Le temps d’une journée de rencontres, puis un jour par semaine : une conférence, un atelier, un séminaire.",
 g12="Une émission découverte du Campus Transitions",
 l12=["La direction du campus et de Polytech Marseille","Un étudiant et un salarié en formation","Un industriel partenaire","Un entretien avec un enseignant-chercheur","Le technopôle de Château-Gombert"])

# ---------- assemblage ----------
CSS=tpl[tpl.index('<style>'):tpl.index('</style>')+8].replace('</style>','.title{text-wrap:balance}\n.ia .iph img,.bn .ph1 img{filter:none}\n</style>')

def build(c):
    LG=f'<div class="lg" style="font-weight:700;font-size:1.3cqw;letter-spacing:.04em;align-self:flex-start">{c["tile"]}</div>'
    def slide(cls,title,body,tsm=True):
        return f'''<section class="slide{(" "+cls) if cls else ""}">
<div class="logo"><i></i>{c["logo"]}</div>
<h2 class="title{" sm" if tsm else ""}">{T(title)}</h2>
<div class="frame"><div class="panel">{T(body)}</div></div>
</section>'''
    tile_ph=lambda k,**kw: photo(k,900,1.4,**kw)
    S=[]
    S.append(f'''<section class="slide">
<div class="logo"><i></i>{c["logo"]}</div>
<h1 class="title">{T(c["cover"])}</h1>
<div class="frame"><div class="panel shot"><img src="{uri(hero(c))}" alt="{c["plat"]}"></div></div>
</section>''')
    co=c['cols']; fan=[photo('A',560,1.3,.5,.5,.85),photo('C',560,1.3,.5,.5,.9),photo('B',560,1.3,.45,.5,.9),photo('F',560,1.3,.8,.6,.75)]
    S.append(slide('warm','Une radio qui capte, forme, invite et informe.',f'''<div class="fanp">
<img class="f f1" src="{fan[0]}" alt=""><img class="f f2" src="{fan[1]}" alt=""><img class="f f3" src="{fan[2]}" alt=""><img class="f f4" src="{fan[3]}" alt="">
<h3>Capter, former, tendre le micro, informer.</h3>
<div class="cols">
<div class="col"><h4>Capter</h4><p>{co[0]}</p></div>
<div class="col"><h4>Former</h4><p>{co[1]}</p></div>
<div class="col"><h4>Tendre le micro</h4><p>{co[2]}</p></div>
<div class="col"><h4>Informer</h4><p>{co[3]}</p></div>
</div></div>''',tsm=False))
    S.append(slide('dusk',c['t3'],f'''<div class="tiles c3">
<div class="tile b">{LG}<div class="bottom huge">{c["big3"]}</div></div>
<div class="tile y"><div class="mid">{c["y3"]}</div><div class="tph"><img src="{tile_ph('E',cx=.62,cy=.6,z=.9)}" alt=""></div></div>
<div class="tile g"><div class="bottom mid">{c["g3"]}</div></div>
</div>'''))
    S.append(slide('',c['t4'],f'''<div class="dk bl"><h3>Media-training</h3><div class="cc"><div class="cph"><img src="{photo('D',1100,1.15,.5,.5,.95)}" alt=""></div><p>{c["p4"]}</p></div></div>'''))
    S.append(slide('warm',c['t5'],f'''<div class="dk"><h3>{c["h5"]}</h3><div class="cc"><div class="cph"><img src="{photo('C',1100,1.15,.5,.42,.68)}" alt=""></div><p>{c["p5"]}</p></div></div>'''))
    S.append(slide('dusk',c['t6'],f'''<div class="tiles c3">
<div class="tile g">{LG}<div class="bottom huge">{c["g6"]}</div></div>
<div class="tile y"><div class="mid">{c["y6"]}</div><div class="tph"><img src="{tile_ph('A',cx=.38,cy=.5,z=.82)}" alt=""></div></div>
<div class="tile b"><div class="xl">{c["b6"]}</div></div>
</div>'''))
    S.append(slide('',c['t7'],f'''<div class="tiles c3">
<div class="tile g">{LG}<div class="bottom huge">{c["g7"]}</div></div>
<div class="tile y"><div class="mid">{c["y7"]}</div><div class="tph"><img src="{tile_ph('B',cx=.42,cy=.45,z=.62)}" alt=""></div></div>
<div class="tile b"><div class="xl">Chaque semaine</div></div>
</div>'''))
    S.append(slide('warm',c['t8'],f'''<div class="ia"><h3>{c["h8"]}</h3>
<div class="iph"><img src="{photo('B',1000,25/19,.5,.5,1.0,fx='gray')}" alt=""></div><div class="sq">→</div>
<p>{c["p8"]}</p></div>'''))
    S.append(slide('dusk',c['t9'],f'''<div class="bn">
<div class="k y1"><span>{c["y9"]}</span></div>
<div class="k d1"><p>{c["d9"]}</p></div>
<div class="k l1"></div>
<div class="k ph1"><img src="{photo('F',1300,38/14,.55,.5,1.0,fx='dark')}" alt=""><span>{c["ph9"]}</span></div>
<div class="k g1"><span>{c["g9"]}</span></div>
<div class="k p1"></div></div>'''))
    y10=c.get('y10') or D_S10_Y.format(who=c['who'])
    S.append(slide('',c['t10'],f'''<div class="tiles c3">
<div class="tile g">{LG}<div class="bottom huge">Un plateau radio en direct.</div></div>
<div class="tile y"><div class="mid">{y10}</div><div class="tph"><img src="{tile_ph('F',cx=.82,cy=.7,z=.55)}" alt=""></div></div>
<div class="tile b"><div class="sm">Par exemple, pour {c["jpo"]}</div><div class="mid">{c["jpo_mid"]}</div></div>
</div>'''))
    st=lambda k,**kw: photo(k,800,1.8,**kw)
    S.append(slide('warm','Simplement : un plateau radio mobile.',f'''<div class="st">
<div class="c"><div class="sph"><img src="{st('A',cx=.5,cy=.5,z=.85)}" alt=""></div><div class="n">01</div><h4>On s’installe</h4><p>{c["s11_1"]}</p></div>
<div class="c"><div class="sph"><img src="{st('E',cx=.68,cy=.66,z=.6)}" alt=""></div><div class="n">02</div><h4>On enregistre</h4><p>{c.get("s11_2",D_S11_2)}</p></div>
<div class="c"><div class="sph"><img src="{st('F',cx=.5,cy=.45,z=.8)}" alt=""></div><div class="n">03</div><h4>On diffuse</h4><p>{D_S11_3}</p></div>
</div>''',tsm=False))
    li=''.join(f'<div class="li">{x}</div>' for x in c['l12'])
    S.append(slide('dusk','Et si on enregistrait un premier épisode ?',f'''<div class="tiles c3">
<div class="tile g">{LG}<div class="bottom huge">{c["g12"]}</div></div>
<div class="tile y">{li}</div>
<div class="tile b"><div class="ct">Studio Récitales<br>06 75 14 68 71<br>hello@studiorecitales.fr</div><a class="go" href="mailto:hello@studiorecitales.fr">Planifier le pilote →</a></div>
</div>''',tsm=False))
    title=T(c['cover']).replace('&nbsp;',' ')
    html=f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{CSS}</head><body><main class="deck">

'''+'\n\n'.join(S)+'''

</main></body></html>
'''
    open(OUT,'w',encoding='utf-8').write(html)
    print(OUT,len(html)//1024,'Ko')

# ---------- PDF : une slide = une page 1920×1080 (le CSS @media print du gabarit) ----------
def to_pdf(html_path,pdf_path):
    h=open(html_path,encoding='utf-8').read()
    # le grain SVG du fond serait rastérisé en grosses images à chaque page (11 Mo → 4 Mo sans lui) : on ne garde que le dégradé
    h=re.sub(r'url\("data:image/svg\+xml;utf8,[^"]*"\),','',h)
    with tempfile.TemporaryDirectory() as d:
        tp=os.path.join(d,'print.html'); open(tp,'w',encoding='utf-8').write(h)
        subprocess.run([CHROME,'--no-sandbox','--disable-gpu','--no-pdf-header-footer','--virtual-time-budget=10000',
                        f'--print-to-pdf={os.path.abspath(pdf_path)}','file://'+tp],check=True,capture_output=True)
    print(pdf_path,os.path.getsize(pdf_path)//1024,'Ko')

if __name__=='__main__':
    build(C)
    if PDF: to_pdf(OUT,PDF)
