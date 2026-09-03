#!/usr/bin/env python3
"""
Generates the Dog Grooming USA artwork set as SVG.

The palette below is sampled directly from the brand logo, so the generated
plates, the vector paw mark and the page CSS all stay in step. Every
raster-photo slot on the landing page points at one of these files, so dropping
in a real photograph later is a one-line `src` swap per slot.

Run:  python3 tools/gen_art.py assets/img
"""
import os
import random
import re
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/img"
os.makedirs(OUT, exist_ok=True)

# --- brand palette, sampled from the logo ------------------------------------
NAVY     = "#0A2472"   # logo outline / deepest blue
NAVY_2   = "#103A9E"
BLUE     = "#0B5BD3"   # "DOG" lettering, bandana
BLUE_2   = "#2E7BE8"
ORANGE   = "#F4681B"   # "GROOMING", paw badge
ORANGE_2 = "#FA8A3E"
ORANGE_D = "#D8500A"
GREEN    = "#0A7A32"   # "USA", palms
GREEN_2  = "#12A047"
GOLD     = "#F2B276"   # retriever coat
PAPER    = "#F4F8FD"
PAPER_2  = "#E4EEFA"
WHITE    = "#FFFFFF"

# Background duotone pairs: (base, gradient end, foreground, accent chip)
SCHEMES = [
    (NAVY,     NAVY_2,    WHITE, ORANGE),
    (BLUE,     BLUE_2,    WHITE, WHITE),
    (ORANGE_D, ORANGE,    WHITE, NAVY),
    (GREEN,    GREEN_2,   WHITE, ORANGE),
    (NAVY_2,   BLUE,      WHITE, GREEN_2),
    (PAPER_2,  "#CFE0F5", NAVY,  ORANGE),
]


def luminance(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mute(hexcolor, amount=.62, toward=(126, 132, 142)):
    """Blend a brand colour toward neutral — used for the `before` plates."""
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    mix = lambda c, t: int(round(c + (t - c) * amount))
    return "#%02X%02X%02X" % (mix(r, toward[0]), mix(g, toward[1]), mix(b, toward[2]))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --- the paw-and-heart mark, lifted from the logo ----------------------------
PAW_PAD = ("M50 81.5 C37.5 81.5 27.5 74.8 27.5 66.2 C27.5 58.3 37.5 53.5 50 53.5 "
           "C62.5 53.5 72.5 58.3 72.5 66.2 C72.5 74.8 62.5 81.5 50 81.5 Z")
PAW_TOES = [(27.5, 43.5, 8.0, 10.6, -22), (42.0, 34.5, 8.6, 11.6, -8),
            (58.0, 34.5, 8.6, 11.6, 8),   (72.5, 43.5, 8.0, 10.6, 22)]
HEART = ("M50 75.5 C44.2 71.1 40.5 68.0 40.5 64.4 C40.5 61.7 42.6 60.1 44.9 60.1 "
         "C46.8 60.1 48.5 61.2 50 62.9 C51.5 61.2 53.2 60.1 55.1 60.1 "
         "C57.4 60.1 59.5 61.7 59.5 64.4 C59.5 68.0 55.8 71.1 50 75.5 Z")


def paw(paw_col, heart_col):
    toes = "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{paw_col}" '
        f'transform="rotate({rot} {cx} {cy})"/>'
        for cx, cy, rx, ry, rot in PAW_TOES
    )
    return (f'<path d="{PAW_PAD}" fill="{paw_col}"/>{toes}'
            f'<path d="{HEART}" fill="{heart_col}"/>')


def paw_badge(size=100, rim=NAVY, face_a=BLUE, face_b=BLUE_2,
              paw_col=ORANGE, heart_col=WHITE, edge=WHITE, uid="m"):
    """The square paw badge used as the compact brand mark and favicon."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}" role="img" aria-label="Dog Grooming USA">
  <defs><linearGradient id="pf-{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{face_b}"/><stop offset="1" stop-color="{face_a}"/>
  </linearGradient></defs>
  <rect width="100" height="100" rx="30" fill="{edge}"/>
  <rect x="3.5" y="3.5" width="93" height="93" rx="27" fill="{rim}"/>
  <rect x="8.5" y="8.5" width="83" height="83" rx="23" fill="url(#pf-{uid})"/>
  {paw(paw_col, heart_col)}
</svg>'''


def grain(seed, w, h, ink, count=140, op=0.05):
    """Deterministic speckle so flat fills read as printed stock, not vector."""
    rnd = random.Random(seed)
    dots = "".join(
        f'<circle cx="{round(rnd.uniform(0, w), 1)}" cy="{round(rnd.uniform(0, h), 1)}" '
        f'r="{round(rnd.uniform(0.6, 2.4), 1)}"/>' for _ in range(count)
    )
    return f'<g fill="{ink}" opacity="{op}">{dots}</g>'


# --- line-art motifs ---------------------------------------------------------
def _stroked(body, stroke, w):
    return (f'<g fill="none" stroke="{stroke}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</g>')

def scissors(s, w=5): return _stroked('<path d="M22 14 L66 62"/><path d="M78 14 L34 62"/><circle cx="26" cy="76" r="12"/><circle cx="74" cy="76" r="12"/><path d="M34 68 L50 52 L66 68"/>', s, w)
def comb(s, w=5):     return _stroked('<path d="M16 34 H84 a6 6 0 0 1 6 6 v6 H10 v-6 a6 6 0 0 1 6-6 Z"/><path d="M20 52 V80 M32 52 V84 M44 52 V80 M56 52 V84 M68 52 V80 M80 52 V84"/>', s, w)
def droplet(s, w=5):  return _stroked('<path d="M50 12 C50 12 22 44 22 62 a28 28 0 0 0 56 0 C78 44 50 12 50 12 Z"/><path d="M38 62 a12 12 0 0 0 12 12"/>', s, w)
def bone(s, w=5):     return _stroked('<path d="M30 40 h40"/><path d="M30 60 h40"/><circle cx="22" cy="38" r="11"/><circle cx="22" cy="60" r="11"/><circle cx="78" cy="38" r="11"/><circle cx="78" cy="60" r="11"/>', s, w)
def house(s, w=5):    return _stroked('<path d="M14 50 L50 18 L86 50"/><path d="M24 46 V84 h52 V46"/><path d="M40 84 V62 a10 10 0 0 1 20 0 v22"/>', s, w)
def sparkle(s, w=5):  return _stroked('<path d="M50 14 C54 38 62 46 86 50 C62 54 54 62 50 86 C46 62 38 54 14 50 C38 46 46 38 50 14 Z"/>', s, w)
def palm(s, w=5):     return _stroked('<path d="M50 26 C50 46 48 66 44 86"/><path d="M50 26 C36 18 22 22 14 34"/><path d="M50 26 C64 18 78 22 86 34"/><path d="M50 26 C38 30 28 40 24 54"/><path d="M50 26 C62 30 72 40 76 54"/>', s, w)

ICONS = {"scissors": scissors, "comb": comb, "droplet": droplet, "bone": bone,
         "house": house, "sparkle": sparkle, "palm": palm}


def plate(name, w, h, scheme_i, icon="scissors", label=None, seed=None,
          sweep=True, muted=False):
    """A branded artwork plate standing in for one photograph.

    Built from line art rather than a filled silhouette so it stays crisp at
    hero scale as well as thumbnail scale.
    """
    a, b, fg, accent = SCHEMES[scheme_i % len(SCHEMES)]
    if muted:
        a, b, accent = mute(a), mute(b), mute(accent)
    seed = seed if seed is not None else abs(hash(name)) % 99991
    rnd = random.Random(seed)
    uid = re.sub(r"[^A-Za-z0-9]", "-", name)
    m = min(w, h)

    ax, ay = w * rnd.uniform(0.06, 0.18), h * rnd.uniform(0.88, 1.02)
    arcs = "".join(
        f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="{m*(0.26+i*0.17):.0f}" fill="none" '
        f'stroke="{fg}" stroke-width="{max(1.0, m*0.0035):.1f}" opacity=".14"/>'
        for i in range(4)
    )

    sweep_svg = ""
    if sweep:
        cx, cy = w * rnd.uniform(0.60, 0.80), h * rnd.uniform(0.16, 0.34)
        sweep_svg = (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" '
                     f'r="{m*rnd.uniform(0.44, 0.60):.0f}" fill="{fg}" opacity=".09"/>')

    big = m * 0.46
    bx, by = (w - big) * 0.52, (h - big) * 0.44
    bw = round(100 * (4.6 / (big / m * 100)) * 0.62, 2)

    # Accent chip carrying the paw mark, echoing the logo.
    chip = m * 0.165
    cx2, cy2 = w - chip - m * 0.09, m * 0.09
    chip_paw = WHITE if luminance(accent) < .62 else NAVY

    label_svg = ""
    if label:
        label_svg = (
            f'<path d="M{m*0.09:.0f} {h - m*0.155:.0f} h{m*0.13:.0f}" stroke="{accent}" '
            f'stroke-width="{max(2.0, m*0.011):.1f}" stroke-linecap="round"/>'
            f'<text x="{m*0.09:.0f}" y="{h - m*0.085:.0f}" fill="{fg}" opacity=".85" '
            f'font-family="Inter, Helvetica Neue, Arial, sans-serif" '
            f'font-size="{max(11.0, m*0.052):.0f}" font-weight="600" '
            f'letter-spacing="{max(1.0, m*0.006):.1f}">{esc(label.upper())}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label or name)}">
  <defs>
    <linearGradient id="bg-{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/>
    </linearGradient>
    <clipPath id="clip-{uid}"><rect width="{w}" height="{h}"/></clipPath>
  </defs>
  <g clip-path="url(#clip-{uid})">
    <rect width="{w}" height="{h}" fill="url(#bg-{uid})"/>
    {arcs}
    {sweep_svg}
    <g transform="translate({bx:.1f} {by:.1f}) scale({big/100:.4f})" opacity=".92">
      {ICONS.get(icon, scissors)(fg, bw)}
    </g>
    <rect x="{cx2:.0f}" y="{cy2:.0f}" width="{chip:.0f}" height="{chip:.0f}" rx="{chip*0.30:.0f}" fill="{accent}"/>
    <g transform="translate({cx2:.1f} {cy2:.1f}) scale({chip/100:.4f})">{paw(chip_paw, accent)}</g>
    {label_svg}
    {grain(seed, w, h, fg)}
  </g>
</svg>'''


def write(fname, svg):
    with open(os.path.join(OUT, fname), "w") as f:
        f.write(svg)


# --- brand marks -------------------------------------------------------------
write("logo-mark.svg", paw_badge(96, uid="mark"))
write("favicon.svg", paw_badge(32, uid="fav"))

# --- hero + services ---------------------------------------------------------
write("hero.svg", plate("hero", 1000, 760, 1, icon="scissors",
                        label="Groomed with care", seed=7))
for i, (f, ic, lb) in enumerate([
    ("svc-grooming.svg", "scissors", "Dog grooming"),
    ("svc-daycare.svg",  "bone",     "Dog daycare"),
    ("svc-hotel.svg",    "house",    "Dog hotel"),
]):
    write(f, plate(f, 800, 600, i, icon=ic, label=lb, seed=20 + i))

# --- before / after ----------------------------------------------------------
# Each pair shares a scheme, seed and motif so the comparison slider reads as
# one image changing state. Labels live in the HTML, not the artwork.
for slug, sch, ic in [("poodle", 1, "scissors"), ("pomeranian", 2, "comb"),
                      ("yorkie", 3, "sparkle")]:
    write(f"ba-{slug}-before.svg",
          plate(f"ba-{slug}-before", 760, 760, sch, icon=ic, seed=40 + sch, muted=True))
    write(f"ba-{slug}-after.svg",
          plate(f"ba-{slug}-after", 760, 760, sch, icon=ic, seed=40 + sch))

# --- facility (captions come from the HTML) ----------------------------------
for i, (f, ic) in enumerate([
    ("facility-stations.svg", "scissors"), ("facility-floor.svg", "comb"),
    ("facility-play.svg", "bone"), ("facility-finishing.svg", "sparkle"),
    ("facility-desk.svg", "house"),
]):
    write(f, plate(f, 900, 640, i + 1, icon=ic, seed=60 + i))

# --- gallery -----------------------------------------------------------------
for i, (f, ic, lb) in enumerate([
    ("gallery-01.svg", "scissors", "Transformation"),
    ("gallery-02.svg", "comb",     "In progress"),
    ("gallery-03.svg", "sparkle",  "Finished styling"),
    ("gallery-04.svg", "droplet",  "Bath & coat care"),
    ("gallery-05.svg", "bone",     "Daycare play"),
    ("gallery-06.svg", "comb",     "Grooming detail"),
    ("gallery-07.svg", "palm",     "Happy client"),
    ("gallery-08.svg", "house",    "Our facility"),
    ("gallery-09.svg", "scissors", "Breed styling"),
]):
    write(f, plate(f, 700, 700, i, icon=ic, label=lb, seed=80 + i))

# --- academy + about ---------------------------------------------------------
write("academy.svg", plate("academy", 900, 700, 3, icon="scissors",
                           label="Groomer Artist Academy", seed=101))
write("about.svg", plate("about", 900, 700, 5, icon="palm",
                         label="Since 2017", seed=102))

print(f"wrote {len(os.listdir(OUT))} files to {OUT}")
