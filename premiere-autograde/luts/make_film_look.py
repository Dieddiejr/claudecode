"""
Génère « Film Doux » : un LUT créatif .cube d'inspiration pellicule
(noirs mats, blancs doux, ombres froides, tons moyens chauds, verts olive).

Entrée et sortie en Rec.709 (images déjà corrigées, pas en log).
Usage : python3 make_film_look.py [taille]   (33 par défaut)
"""
import sys
import numpy as np

# Plancher des noirs et plafond des blancs, par canal (R, V, B) :
# noirs légèrement bleutés, blancs doux, à peine mentholés.
BLACK = np.array([0.040, 0.043, 0.060])
WHITE = np.array([0.905, 0.915, 0.900])


def tone_curve(x):
    """Courbe en S douce : pied allongé, épaule qui écrase les hautes lumières."""
    x = np.clip(x, 0.0, 1.0)
    toe = x ** 1.12  # densifie légèrement les ombres
    # épaule : compression progressive au-dessus de 0,6
    k = 1.6
    shoulder = np.where(toe > 0.6, 0.6 + (1 - np.exp(-k * (toe - 0.6))) / k, toe)
    top = 0.6 + (1 - np.exp(-k * 0.4)) / k
    return shoulder / top


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    safe = d > 1e-9
    rc = np.where(safe, (mx - r) / np.where(safe, d, 1), 0)
    gc = np.where(safe, (mx - g) / np.where(safe, d, 1), 0)
    bc = np.where(safe, (mx - b) / np.where(safe, d, 1), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    s = np.where(mx > 1e-9, d / np.where(mx > 1e-9, mx, 1), 0)
    return np.stack([h, s, mx], -1)


def hsv_to_rgb(hsv):
    h, s, v = hsv[..., 0] % 1.0, hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    i = i.astype(int) % 6
    conds = [i == k for k in range(6)]
    r = np.select(conds, [v, q, p, p, t, v])
    g = np.select(conds, [t, v, v, q, p, p])
    b = np.select(conds, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)


def hue_weight(h, center_deg, width_deg):
    """Poids en cloche autour d'une teinte (en degrés), sur le cercle chromatique."""
    d = (h * 360.0 - center_deg + 180.0) % 360.0 - 180.0
    return np.exp(-0.5 * (d / width_deg) ** 2)


def luma(rgb):
    return rgb @ np.array([0.2126, 0.7152, 0.0722])


def film_look(rgb):
    rgb = np.clip(rgb, 0.0, 1.0)

    # 1. Couleurs sélectives : verts vers l'olive, bleus vers le cyan, peaux préservées.
    hsv = rgb_to_hsv(rgb)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    w_green = hue_weight(h, 110, 35)
    w_blue = hue_weight(h, 215, 30)
    w_skin = hue_weight(h, 25, 18)
    w_red = hue_weight(h, 0, 15)
    shift = (-16 * w_green - 10 * w_blue + 4 * w_red) / 360.0
    h = h + shift * np.clip(s * 2.5, 0, 1)
    sat_gain = 0.86 - 0.16 * w_green - 0.06 * w_blue + 0.08 * w_skin + 0.06 * w_red
    s = np.clip(s * sat_gain, 0, 1)
    rgb = hsv_to_rgb(np.stack([h, s, v], -1))

    # 2. Densité façon pellicule : les couleurs saturées s'assombrissent un peu.
    sat = hsv[..., 1]
    rgb = rgb * (1 - 0.10 * sat ** 1.5)[..., None]

    # 3. Courbe de tons sur la luminance (préserve les teintes).
    y0 = luma(rgb)
    y1 = tone_curve(y0)
    ratio = np.where(y0 > 1e-5, y1 / np.maximum(y0, 1e-5), 1.0)
    rgb = rgb * ratio[..., None]
    rgb = np.where((y0 <= 1e-5)[..., None], y1[..., None], rgb)

    # 4. Split-toning : ombres froides, tons moyens chauds et olive, blancs mentholés.
    y = np.clip(luma(rgb), 0, 1)[..., None]
    w_sh = (1 - np.clip(y / 0.4, 0, 1)) ** 2
    w_mid = np.exp(-0.5 * ((y - 0.45) / 0.17) ** 2)
    w_hi = np.clip((y - 0.6) / 0.4, 0, 1) ** 1.5
    rgb = rgb + w_sh * np.array([-0.010, -0.004, 0.022])
    rgb = rgb + w_mid * np.array([0.028, 0.012, -0.030])
    rgb = rgb + w_hi * np.array([-0.008, 0.006, -0.002])

    # 5. Noirs mats et blancs doux.
    rgb = np.clip(rgb, 0, 1)
    return BLACK + (WHITE - BLACK) * rgb


def build_cube(size=33):
    grid = np.linspace(0.0, 1.0, size)
    # ordre .cube : le rouge varie le plus vite, puis le vert, puis le bleu
    b, g, r = np.meshgrid(grid, grid, grid, indexing="ij")
    rgb = np.stack([r, g, b], -1).reshape(-1, 3)
    out = np.clip(film_look(rgb), 0.0, 1.0)
    lines = [
        'TITLE "Film Doux - Claude AutoGrade"',
        f"LUT_3D_SIZE {size}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
    ]
    lines += [f"{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}" for c in out]
    return "\n".join(lines) + "\n", out.reshape(size, size, size, 3)


if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 33
    text, _ = build_cube(size)
    path = f"Film_Doux_{size}.cube"
    with open(path, "w") as f:
        f.write(text)
    print(f"LUT écrit : {path}")
