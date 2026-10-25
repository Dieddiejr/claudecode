import base64, io, re, sys
from PIL import Image

D = '/tmp/claude-0/-home-user-claudecode/d55f370f-e897-5ff1-8a78-5f06389b4871/scratchpad/'
tpl = open(D + 'work/template.html', encoding='utf-8').read()
fonts = open(D + 'work/fonts.css', encoding='utf-8').read()
fx = open(D + 'work/fx.css', encoding='utf-8').read()

cache = {}
def img(spec):
    if spec in cache: return cache[spec]
    parts = spec.split(':')
    name = parts[0]
    path = D + 'img/' + name + ('.png' if name == 'v00' else '.jpg')
    if len(parts) == 1:
        raw = open(path, 'rb').read()
        mime = 'image/png' if path.endswith('.png') else 'image/jpeg'
    else:
        im = Image.open(path).convert('RGB')
        w = int(parts[1])
        if len(parts) > 2:
            ar = float(parts[2]); fxp = float(parts[3]) if len(parts) > 3 else .5
            W, H = im.size
            if W / H > ar:
                nw = int(H * ar); x = int(min(max(W * fxp - nw / 2, 0), W - nw))
                im = im.crop((x, 0, x + nw, H))
            else:
                nh = int(W / ar); im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
        if im.width > w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'JPEG', quality=82, optimize=True, progressive=True)
        raw = b.getvalue(); mime = 'image/jpeg'
    uri = 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())
    cache[spec] = uri
    return uri

def svg(d): return '<svg viewBox="0 0 24 24">' + d + '</svg>'
SIDE = (svg('<path d="M12 20.5s-7.5-4.6-9.2-9.3C1.6 7.8 3.9 4.5 7.3 4.5c2 0 3.6 1.1 4.7 2.8 1.1-1.7 2.7-2.8 4.7-2.8 3.4 0 5.7 3.3 4.5 6.7-1.7 4.7-9.2 9.3-9.2 9.3z"/>')
        + svg('<path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20.5l1.6-5A8.5 8.5 0 1 1 21 11.5z"/>')
        + svg('<path d="M22 3L9.2 13.2"/><path d="M22 3l-6.5 18-3.3-7.8L3.5 9.7z"/>'))
TABS = ('<span>' + svg('<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>') + '</span>'
        + '<span>' + svg('<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M3 8.5h18M8 3l3 5.5M14 3l3 5.5"/><path d="M10 12v5l4.3-2.5z"/>') + '</span>'
        + '<span>' + svg('<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="12" cy="10" r="3"/><path d="M6.5 21c.8-3 3-4.6 5.5-4.6s4.7 1.6 5.5 4.6"/>') + '</span>')
RL = '<svg class="fx-rl" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm5 6v7l6-3.5z"/></svg>'
# Caroline Dinet et Samuel Perraro uniquement
TILE_SRC = ['a01:240:0.75:0.5', 'a00:240:0.75:0.62', 'a02:240:0.75:0.45', 'a04:240:0.75:0.55',
            'a06:240:0.75:0.5', 'a09:240:0.75:0.6', 'a11:240:0.75:0.55', 'a12:240:0.75:0.45',
            'v10:240:0.75:0.5', 'v08:240:0.75:0.5', 'a00:240:0.75:0.3', 'a02:240:0.75:0.75']
TILES = ''.join('<div class="fx-tile"><img alt="" src="{{img:%s}}">%s</div>' % (t, RL) for t in TILE_SRC)

out = (tpl.replace('{{FONTS}}', fonts).replace('{{FX}}', fx)
          .replace('{{ICO_SIDE}}', SIDE).replace('{{ICO_TABS}}', TABS).replace('{{TILES}}', TILES))
out = re.sub(r'\{\{img:([^}]+)\}\}', lambda m: img(m.group(1)), out)
assert '{{' not in out, re.findall(r'\{\{[^}]*\}\}', out)
open(sys.argv[1], 'w', encoding='utf-8').write(out)
print(len(out) // 1024, 'KB')
