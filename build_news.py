#!/usr/bin/env python3
"""Render the front page: 'Thursday 19 November 2026'.

A single 1024x1024 newspaper front page drawn entirely in code with PIL:
33 verified stories from one day, three illustrated leads, ten small
illustrated cards, a numbered world map, a numbered briefs list, a DATE
CHECK strip and a source line. No photos, no copied art, no network.
Run:  python3 build_news.py   -> writes entry.png beside this file.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (18, 18, 18)
PAPER = (252, 250, 244)
RED = (178, 24, 24)
DARKRED = (140, 16, 16)
BLUE = (24, 64, 140)
TEAL = (14, 110, 110)
GOLD = (176, 128, 20)
GREY = (110, 108, 100)
LIGHT = (232, 228, 218)
RULE = (60, 58, 52)

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, s, path, start, max_w, minimum=8):
    """Largest font size (<= start) at which s fits max_w."""
    size = start
    while size > minimum and text_w(draw, s, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def center(draw, cx, y, s, f, fill=INK):
    draw.text((cx - text_w(draw, s, f) / 2, y), s, font=f, fill=fill)


def left(draw, x, y, s, f, fill=INK):
    draw.text((x, y), s, font=f, fill=fill)


def rule(draw, x0, y, x1, w=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)


def stamp(draw, cx, cy, label, size=17, angle=-14, color=RED):
    """A rotated rubber-stamp outline with text, drawn on a temp layer."""
    f = font(SANS_B, size)
    tw = text_w(draw, label, f)
    pad_x, pad_y = 10, 5
    tmp = Image.new("RGBA", (int(tw + pad_x * 2 + 8), size + pad_y * 2 + 8),
                    (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.rectangle([3, 3, tmp.width - 4, tmp.height - 4], outline=color, width=3)
    td.text((pad_x + 1, pad_y + 1), label, font=f, fill=color)
    tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
    draw._image.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)),
                      tmp)


def badge(draw, cx, cy, label, size=15, fill=RED, fg=(255, 255, 255)):
    """Small solid pill badge centred at (cx, cy)."""
    f = font(SANS_B, size)
    tw = text_w(draw, label, f)
    w, h = int(tw + 18), size + 10
    draw.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                           radius=h // 2, fill=fill)
    draw.text((cx - tw / 2, cy - size / 2 - 1), label, font=f, fill=fg)


def flag_us(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                   outline=INK, width=1)
    for i in range(7):
        if i % 2 == 0:
            draw.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                           fill=(178, 34, 52))
    cw, ch = w * 0.4, h * 4 / 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(28, 48, 110))
    for r in range(3):
        for c in range(5):
            px = x + cw * 0.14 + c * cw * 0.72 / 4
            py = y + ch * 0.16 + r * ch * 0.68 / 2
            draw.ellipse([px - 1, py - 1, px + 1, py + 1],
                         fill=(255, 255, 255))


def flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16),
                   outline=INK, width=1)
    cx, cy = x + w * 0.22, y + h * 0.30
    r = max(2.5, h * 0.24)
    pts = []
    for k in range(10):
        ang = math.radians(-90 + k * 36)
        rr = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=(255, 222, 0))
    for fx, fy in [(0.44, 0.14), (0.54, 0.28), (0.50, 0.52), (0.40, 0.64)]:
        sx, sy = x + w * fx, y + h * fy
        sr = max(1.2, h * 0.09)
        draw.polygon([(sx, sy - sr), (sx + sr * 0.4, sy - sr * 0.4),
                      (sx + sr, sy), (sx + sr * 0.4, sy + sr * 0.4),
                      (sx, sy + sr), (sx - sr * 0.4, sy + sr * 0.4),
                      (sx - sr, sy), (sx - sr * 0.4, sy - sr * 0.4)],
                     fill=(255, 222, 0))


def flag_ru(draw, x, y, w, h):
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def flag_mm(draw, x, y, w, h):
    for i, c in enumerate([(254, 203, 0), (52, 143, 65), (234, 40, 41)]):
        draw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    cx, cy = x + w / 2, y + h / 2
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))

# ---------------------------------------------------------------- leads ---
def draw_leader(draw, cx, cy, r, skin, hair, hair_style, suit, tie,
                face_w=1.0, face_h=1.0, brow=(18, 18, 18), mouth="smile",
                eh=8):
    """One cartoon head + shoulders. hair_style: 'blond', 'black', 'grey'.

    face_w/face_h shape the head (broad, round, long); brow is the
    eyebrow colour; mouth is 'smile', 'soft' or 'flat'; eh is the
    eye height in px (narrower eyes for a smaller eh).
    """
    rw, rh = r * face_w, r * face_h
    # shoulders / suit
    draw.pieslice([cx - rw - 6, cy + rh - 8, cx + rw + 6, cy + rh + 46],
                  180, 360, fill=suit)
    # lapels (darker shade of the suit)
    dark = tuple(max(0, c - 14) for c in suit)
    draw.polygon([(cx - 12, cy + rh + 2), (cx - 2, cy + rh + 4),
                  (cx - 8, cy + rh + 20), (cx - 14, cy + rh + 12)],
                 fill=dark)
    draw.polygon([(cx + 12, cy + rh + 2), (cx + 2, cy + rh + 4),
                  (cx + 8, cy + rh + 20), (cx + 14, cy + rh + 12)],
                 fill=dark)
    # neck
    draw.rectangle([cx - 6, cy + rh - 4, cx + 6, cy + rh + 8], fill=skin)
    # shirt + tie
    draw.polygon([(cx - 7, cy + rh + 2), (cx + 7, cy + rh + 2),
                  (cx + 12, cy + rh + 22), (cx, cy + rh + 34),
                  (cx - 12, cy + rh + 22)], fill=(255, 255, 255))
    draw.polygon([(cx - 5, cy + rh + 4), (cx + 5, cy + rh + 4),
                  (cx + 7, cy + rh + 16), (cx, cy + rh + 30),
                  (cx - 7, cy + rh + 16)], fill=tie)
    # head
    draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=skin,
                 outline=INK, width=2)
    # ears
    draw.ellipse([cx - rw - 4, cy - 4, cx - rw + 4, cy + 8], fill=skin,
                 outline=INK, width=1)
    draw.ellipse([cx + rw - 4, cy - 4, cx + rw + 4, cy + 8], fill=skin,
                 outline=INK, width=1)
    # hair
    if hair_style == "blond":
        # tall swept pompadour: cap + side-swept wave over the forehead
        draw.pieslice([cx - rw, cy - rh - 2, cx + rw, cy + 2], 180, 360,
                      fill=hair)
        draw.polygon([(cx - rw, cy - rh + 10), (cx - rw * 0.55, cy - rh - 12),
                      (cx + rw * 0.35, cy - rh - 13),
                      (cx + rw, cy - rh + 2), (cx + rw * 0.6, cy - rh + 4),
                      (cx + rw * 0.1, cy - rh - 2),
                      (cx - rw * 0.5, cy - rh + 2)], fill=hair)
        draw.arc([cx - rw, cy - rh - 2, cx + rw, cy + 2], 180, 360,
                 fill=hair, width=8)
        draw.polygon([(cx - rw, cy - rh + 8), (cx - rw + 12, cy - rh - 6),
                      (cx - rw + 20, cy - rh + 6)], fill=hair)
        draw.rectangle([cx + rw - 4, cy - rh + 4, cx + rw + 1, cy - 2],
                       fill=hair)
    elif hair_style == "black":
        # neat side part: cap, part line, combed strands
        draw.pieslice([cx - rw, cy - rh - 3, cx + rw, cy - 2], 180, 360,
                      fill=hair)
        draw.rectangle([cx - rw, cy - rh + 2, cx - rw + 5, cy - 4],
                       fill=hair)
        draw.rectangle([cx + rw - 5, cy - rh + 2, cx + rw, cy - 4],
                       fill=hair)
        draw.line([(cx - rw * 0.35, cy - rh - 1),
                   (cx - rw * 0.15, cy - rh + 10)], fill=skin, width=2)
        for k in range(3):
            x0 = cx - rw * 0.1 + k * 7
            draw.line([(x0, cy - rh + 2), (x0 + 4, cy - rh + 10)],
                      fill=(60, 60, 60), width=1)
    else:  # grey, short + receding (slightly fuller cap)
        draw.pieslice([cx - rw, cy - rh - 1, cx + rw, cy - rh + 8], 180, 360,
                      fill=hair)
        draw.arc([cx - rw + 1, cy - rh + 1, cx + rw - 1, cy - rh + 16],
                 180, 360, fill=hair, width=8)
        draw.rectangle([cx - rw, cy - rh + 6, cx - rw + 5, cy + 1],
                       fill=hair)
        draw.rectangle([cx + rw - 5, cy - rh + 6, cx + rw, cy + 1],
                       fill=hair)
    # brows + eyes + nose + mouth
    ex = rw * 0.42
    bw = 3 if hair_style == "blond" else 2
    draw.line([(cx - ex - 7, cy - 8), (cx - ex + 7, cy - 10)], fill=brow,
              width=bw)
    draw.line([(cx + ex - 7, cy - 10), (cx + ex + 7, cy - 8)], fill=brow,
              width=bw)
    for sx in (-1, 1):
        draw.ellipse([cx + sx * ex - 4, cy - 2, cx + sx * ex + 4,
                      cy - 2 + eh], fill=(255, 255, 255), outline=INK,
                     width=1)
        draw.ellipse([cx + sx * ex - 1.6, cy, cx + sx * ex + 1.6,
                      cy + 3.2], fill=INK)
    draw.line([(cx, cy + 4), (cx - 2, cy + 12), (cx + 3, cy + 12)],
              fill=(150, 90, 60), width=2)
    if mouth == "smile":
        draw.arc([cx - 10, cy + 12, cx + 10, cy + 25], 15, 165, fill=INK,
                 width=2)
    elif mouth == "soft":
        draw.arc([cx - 7, cy + 13, cx + 7, cy + 23], 20, 160, fill=INK,
                 width=2)
    else:  # flat
        draw.line([(cx - 7, cy + 19), (cx + 7, cy + 19)], fill=INK, width=2)


def lead1_image(draw, x, y, w, h):
    """APEC summit table: three faced leaders, nameplates, three flags."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 214),
                   outline=INK, width=2)
    # backdrop banner
    draw.rectangle([x, y, x + w, y + 22], fill=BLUE)
    center(draw, x + w / 2, y + 4, "APEC 2026  ·  SHENZHEN",
           font(SANS_B, 12), fill=(255, 255, 255))
    # back wall: skyline hint
    for i, bh in enumerate([22, 34, 26, 38, 28]):
        bx = x + 14 + i * 58
        draw.rectangle([bx, y + 58 - bh, bx + 34, y + 58], fill=(196, 188, 168),
                       outline=(150, 144, 128), width=1)
    draw.rectangle([x, y + 58, x + w, y + 62], fill=(150, 144, 128))
    # table
    draw.rectangle([x + 8, y + h - 41, x + w - 8, y + h - 8],
                   fill=(122, 74, 40), outline=INK, width=2)
    draw.rectangle([x + 8, y + h - 41, x + w - 8, y + h - 33],
                   fill=(240, 235, 220))
    # leaders (broader Trump, rounder Xi, longer/narrower Putin)
    specs = [
        ("TRUMP", (244, 196, 150), (238, 198, 70), "blond",
         (32, 40, 64), (178, 24, 24), flag_us,
         dict(face_w=1.06, face_h=1.0, brow=(190, 160, 60),
              mouth="smile", eh=8)),
        ("XI", (238, 205, 170), (20, 20, 20), "black",
         (28, 28, 30), (178, 24, 24), flag_cn,
         dict(face_w=1.08, face_h=0.98, brow=(20, 20, 20),
              mouth="soft", eh=6)),
        ("PUTIN", (240, 205, 175), (170, 170, 165), "grey",
         (40, 48, 66), (24, 64, 140), flag_ru,
         dict(face_w=0.92, face_h=1.08, brow=(120, 120, 115),
              mouth="flat", eh=7)),
    ]
    n = len(specs)
    for i, (name, skin, hair, style, suit, tie, flagfn, kw) in enumerate(specs):
        cx = x + w * (i + 0.5) / n
        cy = y + 65
        draw_leader(draw, cx, cy, 19, skin, hair, style, suit, tie, **kw)
        # nameplate on the table
        px0, py0 = cx - 34, y + h - 37
        draw.rectangle([px0, py0, px0 + 68, py0 + 12], fill=(255, 255, 255),
                       outline=INK, width=1)
        center(draw, cx, py0 + 1, name, font(SANS_B, 9))
        flagfn(draw, cx - 24, y + h - 23, 48, 15)
    # bottom strip
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=RED)
    center(draw, x + w / 2, y + h - 8, "FIRST US–CHINA–RUSSIA SUMMIT",
           font(SANS_B, 8), fill=(255, 255, 255))


def lead2_image(draw, x, y, w, h):
    """World Court: courthouse, scales of justice, Myanmar flag, 9-6."""
    draw.rectangle([x, y, x + w, y + h], fill=(226, 232, 238),
                   outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + 22], fill=(52, 62, 78))
    center(draw, x + w / 2, y + 4, "WORLD COURT  ·  THE HAGUE",
           font(SANS_B, 12), fill=(255, 255, 255))
    # courthouse: pediment + columns
    bx, by, bw, bh = x + 18, y + 28, 150, 64
    draw.polygon([(bx - 8, by + 22), (bx + bw / 2, by), (bx + bw + 8, by + 22)],
                 fill=(200, 196, 182), outline=INK, width=2)
    draw.ellipse([bx + bw / 2 - 7, by + 6, bx + bw / 2 + 7, by + 20],
                 outline=INK, width=2)
    for i in range(4):
        cx = bx + 14 + i * 40
        draw.rectangle([cx - 6, by + 24, cx + 6, by + bh - 8],
                       fill=(240, 236, 222), outline=INK, width=1)
    draw.rectangle([bx - 6, by + bh - 8, bx + bw + 6, by + bh],
                   fill=(200, 196, 182), outline=INK, width=1)
    draw.rectangle([bx - 6, by + 20, bx + bw + 6, by + 26],
                   fill=(200, 196, 182), outline=INK, width=1)
    # scales of justice, right side
    sx, sy = x + w - 62, y + 44
    draw.line([(sx, sy), (sx, sy + 62)], fill=GOLD, width=4)
    draw.line([(sx - 30, sy + 6), (sx + 30, sy + 6)], fill=GOLD, width=3)
    draw.ellipse([sx - 5, sy - 8, sx + 5, sy + 2], fill=GOLD, outline=INK,
                 width=1)
    for sgn in (-1, 1):
        ex = sx + sgn * 30
        draw.line([(ex, sy + 6), (ex, sy + 26)], fill=GOLD, width=2)
        draw.polygon([(ex - 13, sy + 26), (ex + 13, sy + 26), (ex, sy + 40)],
                     outline=GOLD, width=2)
        draw.line([(ex, sy + 40), (ex, sy + 40)], fill=GOLD, width=1)
    draw.rectangle([sx - 16, sy + 62, sx + 16, sy + 68], fill=GOLD,
                   outline=INK, width=1)
    # Myanmar flag + verdict line
    flag_mm(draw, x + 18, y + h - 32, 46, 24)
    left(draw, x + 72, y + h - 28, "MYANMAR  ·  ROHINGYA CASE",
         font(SANS_B, 10), fill=INK)
    left(draw, x + 72, y + h - 14, "REPARATIONS ORDERED",
         font(SANS_B, 10), fill=DARKRED)
    badge(draw, x + w - 32, y + h - 12, "9–6", size=15)


def lead3_image(draw, x, y, w, h):
    """GTA VI lead: big gamepad, gold VI, 13 YEARS ON badge."""
    draw.rectangle([x, y, x + w, y + h], fill=(40, 30, 60),
                   outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + 22], fill=(20, 18, 34))
    center(draw, x + w / 2, y + 4, "GTA VI  ·  OUT TODAY",
           font(SANS_B, 12), fill=(255, 210, 90))
    # neon skyline hint along the bottom
    for i, bh in enumerate([14, 22, 17, 26, 19, 24]):
        bx = x + 10 + i * 52
        draw.rectangle([bx, y + h - bh, bx + 30, y + h],
                       fill=(70, 55, 110), outline=(150, 130, 200), width=1)
    # big gamepad
    cx, cy = x + w / 2, y + 74
    draw.rounded_rectangle([cx - 96, cy - 34, cx + 96, cy + 34], radius=22,
                           fill=(232, 232, 236), outline=INK, width=2)
    center(draw, cx, cy - 30, "VI", font(SERIF, 20), fill=GOLD)
    # d-pad, left
    draw.line([(cx - 72, cy - 6), (cx - 72, cy + 14)], fill=INK, width=5)
    draw.line([(cx - 82, cy + 4), (cx - 62, cy + 4)], fill=INK, width=5)
    # buttons, right
    for dx, dy, c in [(0, 0, RED), (11, -9, (20, 140, 60)),
                      (11, 9, BLUE), (22, 0, GOLD)]:
        draw.ellipse([cx + 52 + dx, cy - 4 + dy, cx + 62 + dx,
                      cy + 6 + dy], fill=c, outline=INK, width=1)
    # sticks
    for sx in (cx - 34, cx + 30):
        draw.ellipse([sx - 7, cy + 14, sx + 7, cy + 28], fill=(90, 90, 100),
                     outline=INK, width=1)
    badge(draw, x + w - 52, y + h - 16, "13 YEARS ON", size=12)

# ------------------------------------------------------- small pictures ---
def small_bg(draw, x, y, w, h, bg):
    draw.rectangle([x, y, x + w, y + h], fill=bg, outline=INK, width=1)


def pic_bridge(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (198, 216, 232))
    # sun + clouds
    draw.ellipse([x + w - 32, y + 5, x + w - 14, y + 23],
                 fill=(255, 200, 60), outline=(200, 150, 0), width=1)
    for cx, cy in [(x + 22, y + 10), (x + 64, y + 7)]:
        draw.ellipse([cx - 11, cy - 3, cx + 3, cy + 4],
                     fill=(255, 255, 255))
        draw.ellipse([cx - 3, cy - 6, cx + 11, cy + 2],
                     fill=(255, 255, 255))
    # water with wave marks
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(90, 130, 170))
    for wx in range(8, int(w) - 8, 22):
        draw.arc([x + wx, y + h - 13, x + wx + 14, y + h - 5], 0, 180,
                 fill=(255, 255, 255), width=1)
    # suspension bridge: two towers, sagging cable, suspenders, deck
    deck_y = y + h - 24
    t1, t2 = x + 36, x + w - 48
    for tx in (t1, t2):
        draw.rectangle([tx, y + 16, tx + 7, deck_y], fill=(120, 120, 125),
                       outline=INK, width=1)
    pts = []
    for i in range(17):
        fx = t1 + 3 + (t2 - t1) * i / 16
        fy = y + 18 + 16 * 4 * (i / 16) * (1 - i / 16)
        pts.append((fx, fy))
    draw.line(pts, fill=INK, width=1)
    for i in (4, 8, 12):
        fx, fy = pts[i]
        draw.line([(fx, fy), (fx, deck_y)], fill=INK, width=1)
    draw.line([(x + 4, deck_y), (x + w - 4, deck_y)], fill=INK, width=3)
    # train crossing the deck, left of the blast
    draw.rectangle([x + 52, y + 30, x + 80, deck_y], fill=(200, 60, 60),
                   outline=INK, width=1)
    for wx in (x + 56, x + 64, x + 72):
        draw.rectangle([wx, y + 32, wx + 5, deck_y - 3],
                       fill=(255, 255, 255))
    # smoke plume + blast star at the strike point
    for sx, sy, sr in [(x + w / 2 - 10, y + 14, 6), (x + w / 2, y + 9, 7),
                       (x + w / 2 + 10, y + 15, 5)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(120, 120, 120), outline=(90, 90, 90), width=1)
    bx, by = x + w / 2, deck_y - 2
    draw.polygon([(bx, by - 7), (bx + 2, by - 2), (bx + 7, by),
                  (bx + 2, by + 2), (bx, by + 7), (bx - 2, by + 2),
                  (bx - 7, by), (bx - 2, by - 2)],
                 fill=(255, 140, 0), outline=(180, 80, 0))


def pic_missile(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (30, 38, 60))
    # stars
    for sx, sy in [(x + 14, y + 8), (x + 40, y + 14), (x + 70, y + 6),
                   (x + 120, y + 10), (x + 160, y + 8), (x + 180, y + 16)]:
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    # skyline with lit windows
    for i, bh in enumerate([26, 38, 30, 44, 34]):
        bx = x + 8 + i * (w - 16) / 5
        bw = (w - 16) / 5 - 4
        draw.rectangle([bx, y + h - bh, bx + bw, y + h],
                       fill=(120, 130, 150))
        draw.rectangle([bx + 3, y + h - bh - 12, bx + 10, y + h - bh],
                       fill=(255, 220, 120))
        for wy in range(2):
            for wx in range(2):
                draw.rectangle([bx + 4 + wx * 9, y + h - bh + 8 + wy * 10,
                                bx + 7 + wx * 9, y + h - bh + 11 + wy * 10],
                               fill=(255, 220, 120))
    # interceptor trail + smoke puffs
    draw.line([(x + 12, y + 14), (x + w - 40, y + 34)], fill=(255, 255, 255),
              width=2)
    for t in (0.25, 0.5, 0.75):
        px = x + 12 + (w - 52) * t
        py = y + 14 + 20 * t
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(200, 200, 200))
    # incoming missile + intercept burst
    draw.polygon([(x + w - 44, y + 28), (x + w - 20, y + 36),
                  (x + w - 44, y + 42)], fill=(255, 200, 60),
                 outline=INK)
    bx, by = x + w - 22, y + 36
    draw.polygon([(bx, by - 8), (bx + 2, by - 2), (bx + 8, by),
                  (bx + 2, by + 2), (bx, by + 8), (bx - 2, by + 2),
                  (bx - 8, by), (bx - 2, by - 2)],
                 fill=(255, 230, 80), outline=(200, 120, 0))
    draw.ellipse([x + 8, y + 10, x + 26, y + 28], outline=(255, 220, 120),
                 width=2)


def pic_cyclone(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (196, 224, 238))
    cx, cy = x + w / 2, y + h / 2 - 4
    for k in range(3):
        r = 12 + k * 11
        draw.arc([cx - r, cy - r, cx + r, cy + r], 40 + k * 50, 300 + k * 50,
                 fill=(24, 64, 140), width=5)
    # rain streaks
    for rx in range(10, int(w) - 6, 18):
        draw.line([(x + rx, y + 8), (x + rx - 4, y + 18)],
                  fill=(120, 150, 190), width=1)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    # ground + two shelters with red roofs
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(120, 170, 120))
    for hx in (x + 12, x + 46):
        draw.rectangle([hx, y + h - 26, hx + 30, y + h - 12],
                       fill=(240, 235, 220), outline=INK, width=1)
        draw.polygon([(hx - 2, y + h - 26), (hx + 15, y + h - 34),
                      (hx + 32, y + h - 26)], fill=(178, 24, 24),
                     outline=INK)
    # bent palm, right
    px = x + w - 24
    draw.line([(px, y + h - 12), (px + 4, y + h - 30)], fill=(90, 60, 30),
              width=3)
    for ang in (200, 250, 290, 330):
        a = math.radians(ang)
        draw.line([(px + 4, y + h - 30),
                   (px + 4 + 12 * math.cos(a), y + h - 30 + 7 * math.sin(a))],
                  fill=(30, 120, 50), width=2)


def pic_gavel(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (232, 226, 210))
    # sound block under the gavel head
    draw.ellipse([x + w - 62, y + 46, x + w - 8, y + 58],
                 fill=(160, 115, 70), outline=INK, width=1)
    draw.ellipse([x + w - 54, y + 48, x + w - 16, y + 54],
                 outline=(90, 60, 30), width=1)
    # gavel: handle + head, with motion lines
    draw.line([(x + 24, y + 22), (x + w - 30, y + 48)], fill=(120, 84, 48),
              width=7)
    for k in range(3):
        draw.line([(x + w - 66 + k * 3, y + 22 + k * 7),
                   (x + w - 58 + k * 3, y + 26 + k * 7)],
                  fill=(120, 84, 48), width=2)
    draw.rectangle([x + w - 52, y + 30, x + w - 18, y + 52],
                   fill=(90, 60, 30), outline=INK, width=2)
    stamp(draw, x + w / 2, y + h - 34, "OVERTURNED", size=11, angle=-12)


def pic_arctic(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (214, 230, 240))
    # aurora bands, kept inside the card
    draw.arc([x + 10, y + 2, x + 90, y + 26], 200, 340,
             fill=(120, 200, 160), width=3)
    draw.arc([x + 20, y + 6, x + 110, y + 30], 200, 340,
             fill=(90, 180, 140), width=2)
    draw.polygon([(x + 10, y + h - 10), (x + 60, y + 16), (x + 110, y + h - 10)],
                 fill=(255, 255, 255), outline=INK, width=1)
    draw.polygon([(x + 90, y + h - 10), (x + 140, y + 26), (x + w - 8, y + h - 10)],
                 fill=(220, 232, 244), outline=INK, width=1)
    draw.ellipse([x + w - 46, y + 8, x + w - 14, y + 40], fill=(255, 220, 120),
                 outline=INK, width=1)
    # water + ice floes along the base
    draw.rectangle([x, y + h - 10, x + w, y + h], fill=(170, 205, 225))
    for fx, fw in [(x + 16, 26), (x + 120, 30), (x + 160, 22)]:
        draw.polygon([(fx, y + h - 8), (fx + fw, y + h - 8),
                      (fx + fw - 6, y + h - 3), (fx + 6, y + h - 3)],
                     fill=(240, 248, 252), outline=INK, width=1)
    # Danish + US flags planted in the snow (20x13, readable at card size)
    for fx, fy, flag in [(x + 30, y + 38, "dk"), (x + 160, y + 39, "us")]:
        draw.line([(fx, fy), (fx, y + h - 10)], fill=INK, width=2)
        if flag == "dk":
            draw.rectangle([fx, fy, fx + 20, fy + 13], fill=(178, 24, 24),
                           outline=INK, width=1)
            draw.line([(fx + 6, fy), (fx + 6, fy + 13)],
                      fill=(255, 255, 255), width=3)
            draw.line([(fx, fy + 6), (fx + 20, fy + 6)],
                      fill=(255, 255, 255), width=3)
        else:
            draw.rectangle([fx, fy, fx + 20, fy + 13], fill=(178, 34, 52),
                           outline=INK, width=1)
            for wy in (fy + 3, fy + 9):
                draw.rectangle([fx, wy, fx + 20, wy + 1],
                               fill=(255, 255, 255))
            draw.rectangle([fx, fy, fx + 8, fy + 7], fill=(28, 48, 110))
    badge(draw, x + w / 2, y + h - 20, "109–0", size=14)


def pic_ipo(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (226, 238, 226))
    # faint grid
    for gy in (y + 14, y + 28, y + 44):
        draw.line([(x + 6, gy), (x + w - 6, gy)], fill=(200, 214, 200),
                  width=1)
    # candlesticks along the bottom, then the rising line over them
    for cx, top, bot, up in [(x + 22, 50, 58, True), (x + 57, 48, 56, True),
                             (x + 92, 50, 57, False),
                             (x + 127, 46, 55, True)]:
        col = (20, 120, 60) if up else (178, 24, 24)
        draw.line([(cx + 5, top - 4), (cx + 5, bot + 4)], fill=INK, width=1)
        draw.rectangle([cx, top, cx + 10, bot], fill=col, outline=INK,
                       width=1)
    pts = [(x + 10, y + h - 14), (x + 46, y + h - 18), (x + 80, y + h - 16),
           (x + 116, y + h - 24), (x + 150, y + h - 22), (x + w - 12, y + 16)]
    draw.line(pts, fill=(20, 120, 60), width=3)
    draw.polygon([(x + w - 26, y + 10), (x + w - 8, y + 16),
                  (x + w - 24, y + 28)], fill=(20, 120, 60))
    left(draw, x + 10, y + 8, "$83", font(SANS_B, 20), fill=DARKRED)
    left(draw, x + 10, y + 32, "NASDAQ DEBUT", font(SANS_B, 9), fill=INK)


def pic_gamepad(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (40, 30, 60))
    draw.rounded_rectangle([x + 28, y + 18, x + w - 28, y + h - 22], radius=16,
                           fill=(230, 230, 235), outline=INK, width=2)
    draw.line([(x + 48, y + 34), (x + 48, y + 52)], fill=INK, width=4)
    draw.line([(x + 39, y + 43), (x + 57, y + 43)], fill=INK, width=4)
    for dx, dy, c in [(0, 0, RED), (10, -8, (20, 140, 60)),
                      (10, 8, BLUE), (20, 0, GOLD)]:
        draw.ellipse([x + w - 78 + dx, y + 32 + dy, x + w - 68 + dx,
                      y + 42 + dy], fill=c, outline=INK, width=1)
    badge(draw, x + w / 2, y + h - 12, "13 YEARS ON", size=10)


def pic_cop_small(draw, x, y, w, h):
    """COP31 as a small card: globe, struck FOSSIL FUELS, $120BN, CUT."""
    small_bg(draw, x, y, w, h, (214, 232, 226))
    gx, gy, gr = x + 26, y + 31, 19
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(64, 130, 200),
                 outline=INK, width=2)
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 340, fill=(40, 150, 80),
             width=5)
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], 20, 110, fill=(40, 150, 80),
             width=5)
    draw.ellipse([gx - 8, gy - gr + 3, gx + 6, gy - gr + 12],
                 fill=(40, 150, 80))
    draw.ellipse([gx - 6, gy + gr - 12, gx + 10, gy + gr - 2],
                 fill=(40, 150, 80))
    # wind turbine, right side
    tx, ty = x + w - 41, y + 40
    draw.line([(tx, ty), (tx, ty - 22)], fill=(90, 90, 90), width=2)
    for ang in (90, 210, 330):
        a = math.radians(ang)
        draw.line([(tx, ty - 22),
                   (tx + 11 * math.cos(a), ty - 22 + 11 * math.sin(a))],
                  fill=(120, 120, 120), width=2)
    s = "FOSSIL FUELS"
    f = font(SANS_B, 10)
    tw = text_w(draw, s, f)
    left(draw, x + 52, y + 8, s, f, fill=(90, 30, 30))
    draw.line([(x + 50, y + 14), (x + 52 + tw + 2, y + 13)], fill=RED, width=2)
    left(draw, x + 52, y + 22, "$120BN", font(SANS_B, 13), fill=DARKRED)
    left(draw, x + 52, y + 38, "ADAPTATION AID", font(SANS_B, 8), fill=INK)
    stamp(draw, x + w - 24, y + 50, "CUT", size=9, angle=-14)


def pic_march(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (240, 228, 200))
    # confetti dots in the sky strip
    for cx, cy, c in [(x + 52, y + 8, RED), (x + 92, y + 6, BLUE),
                      (x + 132, y + 8, (20, 120, 60)),
                      (x + 172, y + 10, GOLD)]:
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)
    # flag on a pole, left
    draw.line([(x + 12, y + 8), (x + 12, y + 40)], fill=INK, width=2)
    draw.polygon([(x + 12, y + 8), (x + 30, y + 13), (x + 12, y + 18)],
                 fill=(178, 24, 24))
    for i in range(5):
        cx = x + 22 + i * (w - 44) / 4
        # raised fists on figures 1 and 3
        if i in (1, 3):
            draw.line([(cx + 8, y + 36), (cx + 16, y + 18)], fill=INK,
                      width=3)
            draw.ellipse([cx + 14, y + 14, cx + 20, y + 20],
                         fill=(220, 180, 140), outline=INK, width=1)
        draw.ellipse([cx - 9, y + 16, cx + 9, y + 34], fill=(220, 180, 140),
                     outline=INK, width=1)
        draw.rectangle([cx - 9, y + 34, cx + 9, y + h - 8],
                       fill=[(178, 24, 24), (24, 64, 140), (20, 120, 60),
                             (176, 128, 20), (120, 60, 140)][i])
    draw.rectangle([x + w / 2 - 52, y + 46, x + w / 2 + 52, y + 62],
                   fill=(255, 255, 255), outline=INK, width=1)
    center(draw, x + w / 2, y + 49, "GENERAL STRIKE", font(SANS_B, 9))


def pic_runner(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (232, 224, 200))
    # track lanes
    draw.rectangle([x, y + h - 18, x + w, y + h], fill=(178, 90, 60))
    draw.line([(x, y + h - 12), (x + w, y + h - 12)], fill=(255, 255, 255),
              width=1)
    draw.line([(x, y + h - 6), (x + w, y + h - 6)], fill=(255, 255, 255),
              width=1)
    # checkered finish post, right
    draw.line([(x + w - 18, y + 14), (x + w - 18, y + h - 18)], fill=INK,
              width=2)
    for k in range(4):
        col = (255, 255, 255) if k % 2 == 0 else INK
        draw.rectangle([x + w - 18, y + 14 + k * 8, x + w - 10,
                        y + 18 + k * 8], fill=col)
    # motion lines behind the runner
    for my in (y + 22, y + 30, y + 38):
        draw.line([(x + 12, my), (x + 34, my)], fill=(150, 140, 120),
                  width=2)
    cx = x + w / 2 - 10
    draw.ellipse([cx - 8, y + 12, cx + 8, y + 28],
                 fill=(200, 150, 110), outline=INK, width=1)
    draw.line([(cx, y + 28), (cx + 4, y + 52)], fill=INK, width=5)
    draw.line([(cx, y + 32), (cx - 26, y + 22)], fill=INK, width=4)
    draw.line([(cx, y + 32), (cx + 26, y + 44)], fill=INK, width=4)
    draw.line([(cx + 4, y + 52), (cx - 20, y + h - 8)],
              fill=INK, width=4)
    draw.line([(cx + 4, y + 52), (cx + 24, y + h - 14)],
              fill=INK, width=4)
    # BANNED stamp: straight (angle=0) and one size smaller, centred low
    # on the track so it sits fully below the lowest motion line (y+38)
    # and fully inside the left/bottom frame, clear of the runner's
    # rear foot and the finish post. A tilted stamp is too tall for the
    # ~22 px band between the motion lines and the frame bottom.
    stamp(draw, x + 34, y + h - 10, "BANNED", size=7, angle=0)


def pic_jobs(draw, x, y, w, h):
    small_bg(draw, x, y, w, h, (238, 232, 222))
    # faint grid
    for gy in (y + 16, y + 30, y + 44):
        draw.line([(x + 8, gy), (x + w - 8, gy)], fill=(210, 206, 196),
                  width=1)
    for i, bh in enumerate([30, 40, 34, 48, 42]):
        bx = x + 16 + i * 30
        draw.rectangle([bx, y + h - 14 - bh, bx + 20, y + h - 14],
                       fill=(24, 64, 140), outline=INK, width=1)
    pts = [(x + 20, y + 38), (x + 60, y + 44), (x + 100, y + 40),
           (x + 140, y + 50), (x + w - 16, y + 48)]
    draw.line(pts, fill=RED, width=3)
    # down arrowhead at the end of the red line
    ex, ey = x + w - 16, y + 48
    draw.polygon([(ex, ey + 8), (ex - 8, ey - 2), (ex + 2, ey - 4)],
                 fill=RED)
    # white chip so the figure stays readable over the bars
    draw.rectangle([x + 8, y + 4, x + 56, y + 26], fill=(255, 255, 255),
                   outline=(200, 196, 186), width=1)
    left(draw, x + 10, y + 6, "4.9%", font(SANS_B, 18), fill=DARKRED)


# ------------------------------------------------------------ world map ---
# More faithful continent outlines in map-local coords (0..300 x 0..140),
# plus Greenland, the UK, Japan, the Indonesian islands, the
# Philippines, New Guinea, Madagascar, Tasmania and New Zealand.
CONTINENTS = {
    "NA": [(2, 10), (13, 4), (38, 5), (63, 7), (75, 14), (92, 22),
           (98, 29), (92, 33), (78, 40), (74, 54), (67, 50), (60, 54),
           (54, 60), (62, 66), (70, 69), (75, 71), (70, 68), (66, 65),
           (60, 62), (54, 59), (50, 56), (47, 51), (42, 44), (38, 36),
           (37, 28), (33, 22), (25, 16), (15, 18), (4, 16)],
    "GL": [(93, 12), (104, 5), (117, 2), (125, 1), (121, 5), (108, 8),
           (96, 16)],
    "SA": [(75, 69), (83, 68), (92, 72), (100, 81), (112, 89), (110, 97),
           (108, 104), (102, 111), (96, 118), (90, 125), (85, 135),
           (83, 139), (81, 128), (81, 116), (82, 102), (77, 94),
           (75, 85), (74, 78)],
    "UK": [(138, 27), (139, 24), (138, 21), (139, 18), (141, 19),
           (142, 24), (142, 26)],
    "EU": [(134, 41), (134, 35), (140, 33), (141, 31), (142, 27),
           (144, 26), (148, 23), (148, 19), (151, 18), (157, 20),
           (159, 22), (162, 18), (165, 16), (167, 14), (168, 10),
           (175, 8), (178, 12), (175, 16), (171, 18), (167, 22),
           (165, 24), (161, 27), (157, 29), (155, 31), (153, 32),
           (152, 33), (155, 37), (157, 40), (154, 41), (152, 38),
           (148, 33), (144, 34), (142, 38), (140, 41)],
    "AF": [(128, 65), (128, 59), (133, 47), (138, 43), (142, 42),
           (150, 41), (154, 46), (158, 46), (162, 46), (167, 47),
           (168, 50), (171, 51), (174, 58), (178, 68), (182, 69),
           (184, 68), (182, 79), (177, 83), (175, 92), (172, 100),
           (169, 109), (165, 116), (158, 118), (156, 115), (153, 104),
           (152, 100), (149, 82), (149, 76), (135, 75), (131, 72),
           (128, 68)],
    "MG": [(178, 98), (181, 102), (181, 108), (178, 108), (177, 102)],
    "AS": [(175, 8), (192, 5), (208, 2), (225, 2), (242, 2), (258, 3),
           (275, 5), (283, 10), (290, 11), (283, 16), (277, 20),
           (273, 25), (267, 31), (260, 27), (259, 33), (256, 40),
           (250, 43), (247, 45), (243, 48), (242, 54), (238, 56),
           (233, 59), (232, 61), (230, 70), (228, 71), (225, 72),
           (223, 68), (222, 64), (220, 63), (218, 58), (216, 57),
           (213, 59), (210, 62), (208, 67), (206, 72), (204, 68),
           (202, 62), (200, 59), (197, 54), (193, 54), (190, 54),
           (188, 53), (185, 51), (183, 50), (182, 48), (178, 50),
           (175, 47), (172, 42), (169, 42), (167, 42), (164, 41),
           (163, 40), (161, 38), (158, 36), (165, 32), (172, 30),
           (178, 28), (183, 26), (188, 22), (192, 18), (196, 14),
           (192, 10), (183, 8), (179, 8)],
    "JP": [(250, 47), (252, 44), (256, 43), (257, 40), (259, 36),
           (261, 33), (259, 32), (257, 38), (254, 44), (251, 45)],
    "ID": [(221, 75), (225, 81), (228, 85), (230, 87), (227, 83),
           (224, 78)],
    "JV": [(229, 87), (235, 88), (237, 89), (232, 89)],
    "BN": [(232, 80), (236, 77), (239, 79), (240, 83), (238, 85),
           (234, 84)],
    "PH": [(242, 61), (243, 66), (242, 70)],
    "NG": [(251, 82), (255, 83), (259, 85), (263, 87), (259, 89),
           (255, 88)],
    "OC": [(236, 104), (237, 113), (240, 119), (249, 115), (254, 119),
           (258, 122), (263, 123), (267, 121), (269, 115), (269, 110),
           (267, 105), (263, 101), (260, 93), (256, 94), (252, 94),
           (247, 96), (243, 96), (239, 102)],
    "TS": [(262, 125), (265, 126), (264, 127)],
    "NZ": [(281, 129), (285, 125), (288, 121), (290, 121), (288, 124),
           (283, 127)],
}
# (map x, map y, number) pins: one per ALSO ON brief, numbered 14-33
# to match that list. 15 (Albanese at APEC) sits on SE Australia;
# 33 (space) is a star-marked pin over the Pacific, top right.
PINS = [(237, 57, 14), (266, 118, 15), (247, 40, 16), (231, 88, 17),
        (188, 53, 18), (170, 47, 19), (180, 32, 20), (145, 29, 21),
        (140, 22, 22), (155, 24, 23), (153, 36, 24), (179, 79, 25),
        (168, 64, 26), (165, 109, 27), (128, 51, 28), (74, 53, 29),
        (288, 125, 30), (288, 103, 31), (12, 103, 32), (288, 12, 33)]
# (map x, map y, label) small continent names.
LABELS = [(38, 16, "NORTH AMERICA"), (82, 92, "SOUTH AMERICA"),
          (152, 10, "EUROPE"), (158, 72, "AFRICA"), (228, 28, "ASIA"),
          (250, 106, "AUSTRALIA"), (48, 108, "PACIFIC")]
# gold stars marking the space story (33) in the top-right corner.
STARS = [(276, 6), (296, 22), (272, 22)]


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 232, 240),
                   outline=INK, width=2)
    sx, sy = w / 300.0, h / 140.0
    for pts in CONTINENTS.values():
        poly = [(x + px * sx, y + py * sy) for px, py in pts]
        draw.polygon(poly, fill=(190, 196, 182), outline=(90, 92, 84))
    # graticule
    for gx in range(0, 301, 60):
        draw.line([(x + gx * sx, y), (x + gx * sx, y + h)],
                  fill=(255, 255, 255), width=1)
    for gy in range(0, 141, 35):
        draw.line([(x, y + gy * sy), (x + w, y + gy * sy)],
                  fill=(255, 255, 255), width=1)
    for lx, ly, name in LABELS:
        center(draw, x + lx * sx, y + ly * sy - 4, name, font(SANS_B, 8),
               fill=(96, 98, 90))
    for sx_, sy_ in STARS:
        cx, cy = x + sx_ * sx, y + sy_ * sy
        draw.polygon([(cx, cy - 4), (cx + 1.4, cy - 1.4), (cx + 4, cy),
                      (cx + 1.4, cy + 1.4), (cx, cy + 4),
                      (cx - 1.4, cy + 1.4), (cx - 4, cy),
                      (cx - 1.4, cy - 1.4)], fill=(255, 210, 60),
                     outline=(176, 128, 20))
    for px, py, num in PINS:
        cx, cy = x + px * sx, y + py * sy
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                     outline=(255, 255, 255), width=1)
        center(draw, cx, cy - 4, str(num), font(SANS_B, 8),
               fill=(255, 255, 255))

# ------------------------------------------------------------------ data ---
LEADS = [
    dict(pic="summit", tag="SUMMIT · SHENZHEN",
         head="Three leaders, one table in Shenzhen",
         deck=("Trump, Xi and Putin meet for the first time, talking "
               "nuclear arms, peace and UN reform. Xi urges a "
               "nuclear-weapons ban."),
         src="Reuters · AP · Xinhua"),
    dict(pic="court", tag="THE HAGUE · VERDICT",
         head="World Court: Myanmar guilty of genocide",
         deck=("Judges in The Hague rule 9–6 that Myanmar's 2017 campaign "
               "against the Rohingya was genocide, and order reparations."),
         src="Al Jazeera · UN News"),
    dict(pic="gta", tag="GAMES · VICE CITY",
         head="GTA VI is out — after 13 years",
         deck=("Thirteen years of waiting end at midnight, with queues "
               "outside shops and first reviews hailing the return to "
               "Vice City."),
         src="ABC"),
]

SMALL = [
    dict(pic=pic_cop_small, tag="CLIMATE", head="COP31 draft drops fossil fuels",
         deck="Draft cuts fossil fuels and sets $120bn in adaptation aid.",
         src="Reuters · AFP"),
    dict(pic=pic_bridge, tag="UKRAINE", head="Kyiv hits Kerch Bridge again",
         deck="A third strike in a week halts rail traffic to Russia.",
         src="Euronews"),
    dict(pic=pic_missile, tag="RIYADH", head="Saudi shield stops Houthi missile",
         deck="Debris falls on the capital; no casualties reported.",
         src="Reuters"),
    dict(pic=pic_cyclone, tag="INDIA", head="Cyclone Akvan bears down on India",
         deck="100,000+ move to shelters in Odisha before Friday landfall.",
         src="IMD"),
    dict(pic=pic_gavel, tag="SEOUL", head="Seoul court voids martial-law verdict",
         deck="High court overturns the ruling against ex-PM Han Duck-soo.",
         src="AP"),
    dict(pic=pic_arctic, tag="ARCTIC", head="Denmark backs Arctic pact with US",
         deck="Parliament approves the deal by 109 votes to none.",
         src="AP"),
    dict(pic=pic_ipo, tag="WALL STREET", head="Anthropic's $83 debut sets IPO record",
         deck="Nasdaq listing raises $81.3bn, the largest on record.",
         src="AP"),
    dict(pic=pic_march, tag="COLOMBIA", head="Colombia stops work in national strike",
         deck="Unions march through three cities.",
         src="Infobae"),
    dict(pic=pic_runner, tag="KENYA", head="Kenyan marathon champion banned 3 years",
         deck="A doping ban ends the champion's run.",
         src="ABC"),
    dict(pic=pic_jobs, tag="AUSTRALIA", head="Australia jobless rate hits 4.9%",
         deck="Highest since 2024; shares and the dollar fall.",
         src="ABC"),
]

BRIEFS = [
    (14, "SHENZHEN", "Xi presses for a nuclear-weapons ban.", "Al Jazeera"),
    (15, "APEC", "Albanese to Putin: \u201cEnd your war, end it now.\u201d", "ABC"),
    (16, "SEOUL", "551,864 pupils sit the Suneung exam; planes grounded.", "Sedaily"),
    (17, "JAKARTA", "Asset-seizure law passes after 18 years.", "Kompas"),
    (18, "HORMUZ", "Iran lays mines; three tankers burn.", "Al Jazeera"),
    (19, "GAZA", "Israel ends tank push past the ceasefire line.", "BBC"),
    (20, "KRASNODAR", "Kyiv claims strikes on two oil refineries.", "Euronews"),
    (21, "BRUSSELS", "EU delays methane rules by two years.", "Euronews"),
    (22, "ENGLAND", "Inquiry: Bayesian yacht was vulnerable to wind.", "RNZ"),
    (23, "ZURICH", "Two rivals challenge Infantino at FIFA.", "ABC"),
    (24, "ROME", "Writer Corrado Augias dies aged 91.", "Euronews"),
    (25, "MOGADISHU", "Somalia expels the UAE ambassador.", "Al Jazeera"),
    (26, "SUDAN", "Court sentences RSF chief to death in absentia.", "AP"),
    (27, "PRETORIA", "Central bank holds rates at 7.25%.", "SABC"),
    (28, "CANARIES", "Record 11,000 migrants in 15 days.", "Africanews"),
    (29, "FLORIDA", "Floods shut Broward; Miami schools close again.", "CBS"),
    (30, "WELLINGTON", "Court: pay-equity cuts broke the law.", "RNZ"),
    (31, "TONGA", "Drought emergency comes into force.", "RNZ"),
    (32, "COOK ISLANDS", "Cyclone Xavier weakens to category 4.", "RNZ"),
    (33, "SPACE", "Red giant seen swallowing a Sun-sized star.", "Nature"),
]

REGIONS = [("ASIA", 7, (178, 24, 24)), ("MIDDLE EAST", 3, (24, 64, 140)),
           ("EUROPE", 7, (20, 120, 60)), ("AFRICA", 5, (176, 128, 20)),
           ("AMERICAS", 4, (120, 60, 140)), ("OCEANIA", 4, (14, 110, 110)),
           ("GLOBAL", 3, (90, 90, 90))]


# --------------------------------------------------------------- layout ---
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx, right = 14, W - 14

    # kicker
    f_kick = font(SANS_B, 12)
    left(d, mx, 8, "THE WORLD IN ONE DAY", f_kick)
    s = "33 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY"
    draw_right = right - text_w(d, s, f_kick)
    left(d, draw_right, 8, s, f_kick)
    rule(d, mx, 26, right, 2)

    # masthead
    f_mast = font(SERIF, 46)
    center(d, W / 2, 30, "Thursday 19 November 2026", f_mast)
    rule(d, mx, 84, right, 3)

    # red sub-headline
    sub = ("TRUMP · XI · PUTIN MEET IN SHENZHEN  —  ICJ: MYANMAR GUILTY "
           "OF GENOCIDE  —  GTA VI OUT AFTER 13 YEARS")
    f_sub = fit_font(d, sub, SANS_B, 15, right - mx)
    center(d, W / 2, 90, sub, f_sub, fill=RED)
    rule(d, mx, 110, right, 1)

    # continent bar
    bx, by, bw, bh = mx, 116, right - mx, 20
    x = bx
    for name, n, col in REGIONS:
        seg = bw * n / 33
        d.rectangle([x, by, x + seg, by + bh], fill=col, outline=PAPER, width=1)
        x += seg
    stats = "  ·  ".join(f"{n} {c}" for n, c, _ in
                         [(r[0], r[1], r[2]) for r in REGIONS])
    stats = "ASIA 7  ·  MIDDLE EAST 3  ·  EUROPE 7  ·  AFRICA 5  ·  " \
            "AMERICAS 4  ·  OCEANIA 4  ·  GLOBAL 3  ·  COP31 AID $120BN"
    center(d, W / 2, 140, stats, font(SANS_B, 11))
    rule(d, mx, 158, right, 1)

    # three leads
    ly, lh = 166, 226
    cw = (right - mx - 24) / 3
    for i, lead in enumerate(LEADS):
        x0 = mx + i * (cw + 12)
        if i:
            d.line([(x0 - 6, ly), (x0 - 6, ly + lh)], fill=LIGHT, width=1)
        ih = 132
        if lead["pic"] == "summit":
            lead1_image(d, x0, ly, cw, ih)
        elif lead["pic"] == "court":
            lead2_image(d, x0, ly, cw, ih)
        else:
            lead3_image(d, x0, ly, cw, ih)
        ty = ly + ih + 6
        left(d, x0, ty, lead["tag"], font(SANS_B, 10), fill=RED)
        f_h = font(SERIF, 17)
        lines = wrap(d, lead["head"], f_h, cw)
        yy = ty + 14
        for ln in lines[:2]:
            left(d, x0, yy, ln, f_h)
            yy += 20
        f_deck = font(SANS, 10)
        yy += 2
        for ln in wrap(d, lead["deck"], f_deck, cw)[:2]:
            left(d, x0, yy, ln, f_deck)
            yy += 12
        left(d, x0, yy + 3, lead["src"], font(SANS, 9), fill=GREY)

    # ten small cards, two rows of five
    sy0, sh, sw = 400, 140, (right - mx - 40) / 5
    for row in range(2):
        for col in range(5):
            card = SMALL[row * 5 + col]
            x0 = mx + col * (sw + 10)
            y0 = sy0 + row * (sh + 8)
            card["pic"](d, x0, y0, sw, 62)
            yy = y0 + 68
            left(d, x0, yy, card["tag"], font(SANS_B, 8), fill=RED)
            f_h = font(SANS_B, 11)
            lines = wrap(d, card["head"], f_h, sw)
            yy += 11
            for ln in lines[:2]:
                left(d, x0, yy, ln, f_h)
                yy += 13
            f_deck = font(SANS, 9)
            for ln in wrap(d, card["deck"], f_deck, sw)[:2]:
                left(d, x0, yy, ln, f_deck)
                yy += 11
            left(d, x0, y0 + sh - 11, card["src"], font(SANS, 8), fill=GREY)

    # map + briefs header
    hy = 692
    rule(d, mx, hy, right, 2)
    left(d, mx, hy + 6, "WHERE IT HAPPENED", font(SANS_B, 13))
    left(d, 368, hy + 6, "ALSO ON THURSDAY 19 NOVEMBER 2026",
         font(SANS_B, 13))

    # map (left) and numbered briefs (right)
    my, mh = 716, 232
    draw_map(d, mx, my, 330, mh)
    d.rectangle([mx, my + mh - 18, mx + 330, my + mh], fill=(255, 255, 255))
    center(d, mx + 165, my + mh - 15, "19 NOVEMBER 2026 · 6 CONTINENTS",
           font(SANS_B, 9), fill=INK)
    bx0, bw2 = 368, right - 368
    f_b = font(SANS, 10)
    f_bn = font(SANS_B, 10)
    for i, (num, city, head, src) in enumerate(BRIEFS):
        yy = my + 2 + i * 11.6
        left(d, bx0, yy, f"{num}", f_bn, fill=RED)
        line = f"{city} — {head} {src}"
        left(d, bx0 + 24, yy, line, f_b)

    # DATE CHECK + footer
    fy = 956
    rule(d, mx, fy, right, 2)
    f_dc = font(SANS_B, 10)
    left(d, mx, fy + 6,
         "DATE CHECK — Every story on this page happened, or was first "
         "reported, on Thursday 19 November 2026.", f_dc)
    dc2 = ("LEFT OUT AS OTHER DAYS' NEWS:  18 NOV: EU's €45bn Ukraine loan "
           "plan · Iran fires on Kuwait and Bahrain · Nvidia results · "
           "Jeffries named for US speaker · Carney on China ties ·  "
           "20 NOV: COP31's scheduled close · Cyclone Akvan's landfall")
    yy = fy + 22
    for ln in wrap(d, dc2, font(SANS, 9), right - mx):
        left(d, mx, yy, ln, font(SANS, 9), fill=INK)
        yy += 11
    rule(d, mx, 1002, right, 1)
    foot = ("Claims are attributed, not stated as fact · Pictures and map: "
            "original, drawn in code · Sources: Reuters, AP, AFP, BBC, "
            "Al Jazeera, UN News, Euronews, ABC, RNZ, Xinhua, Nature · "
            "2026-11-19")
    center(d, W / 2, 1007, foot, font(SANS, 8), fill=GREY)

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    render()
