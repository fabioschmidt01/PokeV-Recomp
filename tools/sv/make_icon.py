"""PokeV-Recomp's icon: docs/icon/icon_1024.png (window icon at run time), docs/icon/icon.ico (the .exe's) and
docs/icon/icon.icns (macOS bundle).
An original drawing in the start screen's own style and palette (runtime/ui/launcher.mm draw_art: a violet night sky,
an aurora, a crescent moon, a mountain with a crater and a cyan light rising from it through rings and a hexagon) and
"PV" in the start screen's gold. Violet and a touch of the future for Pokémon Violet; no game artwork, logo or
character. Lettering: Baloo 2 SemiBold (OFL, third_party/fonts/Baloo2). Needs Pillow.
Usage: python tools/sv/make_icon.py
"""
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
S = 4096  # drawn at 4x, downsampled (anti-aliasing)
M, R = 400, 720  # margin and corner radius of the rounded square (as ZA Recomp's icon: 100 / 180 at 1024)
GOLD = (242, 181, 68)   # (the start screen's accent: its buttons, this icon's letters and edge)
CYAN = (110, 230, 255)  # (the light from the crater)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def vgradient(w, h, stops):
    """A vertical gradient through (position 0..1, colour) stops: one column, stretched (per-pixel loops are slow at 4x)."""
    col = Image.new('RGBA', (1, h))
    px = col.load()
    for y in range(h):
        t = y / (h - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t <= t1:
                px[0, y] = lerp(c0, c1, (t - t0) / (t1 - t0)) + (255,)
                break
    return col.resize((w, h))


def glow(size, box, colour, alpha, blur):
    g = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse(box, fill=colour + (alpha,))
    return g.filter(ImageFilter.GaussianBlur(blur))


def ridge(rnd, w, h, y_lo, y_hi, step, jag):
    """A mountain silhouette across the picture: a polygon from a jagged line between y_lo and y_hi (fractions of h)."""
    pts, x, y = [], -step, rnd.uniform(y_lo, y_hi)
    while x < w + step:
        pts.append((x, int(h * y)))
        x += rnd.randrange(step // 2, step)
        y = min(y_hi, max(y_lo, y + rnd.uniform(-jag, jag)))
    return pts + [(w + step, h), (-step, h)]


def main():
    w = h = S - 2 * M
    # the start screen's sky: near black, through deep violet, to a lighter violet at the horizon
    art = vgradient(w, h, [(0, (9, 6, 24)), (0.50, (26, 15, 58)), (0.82, (52, 28, 96)), (1, (78, 44, 120))])
    art.alpha_composite(glow((w, h), (-700, -500, 1900, 1500), (124, 92, 255), 80, 330))   # the violet aurora, up left
    art.alpha_composite(glow((w, h), (-900, -700, 700, 500), (64, 224, 232), 50, 300))     # its cyan edge
    d = ImageDraw.Draw(art)
    rnd = random.Random(11)
    for _ in range(46):  # stars
        x, y, r = rnd.randrange(w), rnd.randrange(int(h * 0.5)), rnd.choice((5, 7, 9, 13))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(232, 226, 250, rnd.randrange(130, 255)))

    # the crescent moon, up right: a disc less a shifted one (as the start screen's), with a faint halo
    mx, my, mr = int(w * 0.80), int(h * 0.17), 250
    art.alpha_composite(glow((w, h), (mx - 420, my - 420, mx + 420, my + 420), (244, 230, 191), 46, 150))
    moon = Image.new('L', (w, h), 0)
    ImageDraw.Draw(moon).ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=255)
    cut = Image.new('L', (w, h), 0)
    ImageDraw.Draw(cut).ellipse((mx - mr + 120, my - mr - 80, mx + mr + 120, my + mr - 80), fill=255)
    art.paste(Image.new('RGBA', (w, h), (244, 230, 191, 255)), (0, 0), ImageChops.subtract(moon, cut))

    # far mountains, then the violet glow behind the crater and the light rising from it (the start screen's beam)
    d = ImageDraw.Draw(art)
    d.polygon(ridge(random.Random(5), w, h, 0.46, 0.60, 420, 0.07), fill=(36, 22, 78, 255))
    cx = int(w * 0.5)
    art.alpha_composite(glow((w, h), (cx - 1300, int(h * 0.36), cx + 1300, int(h * 1.05)), (124, 92, 255), 110, 300))
    beam = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    rim = int(h * 0.50)  # the crater's rim
    bcol = Image.new('RGBA', (170, rim), CYAN + (255,))
    bcol.putalpha(Image.linear_gradient('L').resize((170, rim)).point(lambda v: int(v * 0.72)))  # (fades upward)
    beam.paste(bcol, (cx - 85, 0))
    art.alpha_composite(beam.filter(ImageFilter.GaussianBlur(36)))

    # the mountain: a dark massif with a crater at the top and a lit left face, the light's rings widening upward
    # inside a faint hexagon (the start screen's), and the glow at the crater's mouth
    d = ImageDraw.Draw(art)
    base = int(h * 0.84)
    massif = [(cx - 1650, base), (cx - 1180, int(h * 0.72)), (cx - 900, int(h * 0.74)), (cx - 600, int(h * 0.60)),
              (cx - 420, int(h * 0.62)), (cx - 230, int(h * 0.51)), (cx - 150, int(h * 0.53)), (cx - 70, rim - 40),
              (cx, int(h * 0.535)), (cx + 70, rim - 40), (cx + 160, int(h * 0.54)), (cx + 250, int(h * 0.52)),
              (cx + 470, int(h * 0.63)), (cx + 640, int(h * 0.61)), (cx + 930, int(h * 0.74)), (cx + 1170, int(h * 0.72)),
              (cx + 1650, base)]
    d.polygon(massif, fill=(20, 11, 48, 255))
    d.polygon([(cx - 70, rim - 40), (cx - 150, int(h * 0.53)), (cx - 230, int(h * 0.51)), (cx - 420, int(h * 0.62)),
               (cx - 300, int(h * 0.61)), (cx - 200, int(h * 0.565)), (cx - 130, int(h * 0.60)), (cx - 40, int(h * 0.52))],
              fill=(46, 28, 98, 255))
    lines = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lines)
    ld.regular_polygon((cx, int(h * 0.335), 560), 6, outline=CYAN + (70,), width=14)
    for y, half, a in ((0.455, 190, 235), (0.385, 290, 180), (0.300, 410, 125)):
        yy, hh = int(h * y), int(half * 0.2)
        ld.ellipse((cx - half, yy - hh, cx + half, yy + hh), outline=CYAN + (a,), width=24)
    art.alpha_composite(lines)
    art.alpha_composite(glow((w, h), (cx - 230, rim - 230, cx + 230, rim + 190), CYAN, 150, 80))
    d = ImageDraw.Draw(art)
    d.ellipse((cx - 32, rim - 32, cx + 32, rim + 32), fill=(214, 246, 255, 255))

    # nearer hills in front, darkest last, with a row of small lights along the foot (the start screen's)
    d.polygon(ridge(random.Random(8), w, h, 0.76, 0.83, 520, 0.04), fill=(22, 13, 52, 255))
    d.polygon(ridge(random.Random(2), w, h, 0.85, 0.90, 640, 0.03), fill=(9, 5, 24, 255))
    for i in range(9):
        x, y = int(w * (0.06 + i * 0.11)), int(h * (0.885 if i & 1 else 0.875))
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=CYAN + (170 if i & 1 else 210,))

    # "PV": gold to orange, a soft shadow, in the lower band
    font = ImageFont.truetype(os.path.join(ROOT, 'third_party', 'fonts', 'Baloo2', 'Baloo2-SemiBold.ttf'), 1150)
    text = 'PV'
    box = d.textbbox((0, 0), text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    tx, ty = (w - tw) // 2 - box[0], int(h * 0.965) - th - box[1]
    shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((tx + 30, ty + 40), text, font=font, fill=(0, 0, 0, 215))
    art.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(40)))
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).text((tx, ty), text, font=font, fill=255)
    top = (ty + box[1]) / h
    grad = vgradient(w, h, [(0, (255, 236, 130)), (top, (255, 236, 130)), (top + th / h, (255, 132, 44)), (1, (255, 132, 44))])
    art.paste(grad, (0, 0), mask)

    # rounded square with a thin gold edge, on a transparent canvas
    shape = Image.new('L', (w, h), 0)
    ImageDraw.Draw(shape).rounded_rectangle((0, 0, w - 1, h - 1), R, fill=255)
    edge = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle((14, 14, w - 15, h - 15), R - 14, outline=GOLD + (120,), width=28)
    art.alpha_composite(edge)
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(art, (M, M), shape)
    out = out.resize((1024, 1024), Image.LANCZOS)
    icon_dir = os.path.join(ROOT, 'docs', 'icon')
    out.save(os.path.join(icon_dir, 'icon_1024.png'))
    out.save(os.path.join(icon_dir, 'icon.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128),
                                                       (256, 256)])
    out.save(os.path.join(icon_dir, 'icon.icns'))
    print('docs/icon/icon_1024.png, docs/icon/icon.ico, docs/icon/icon.icns')


if __name__ == '__main__':
    main()
