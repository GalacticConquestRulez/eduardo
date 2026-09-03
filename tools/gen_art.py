#!/usr/bin/env python3
"""
Generates the Dog Grooming USA brand artwork set as SVG.

Every raster-photo slot on the landing page points at one of these files, so
dropping in a real photograph later is a one-line `src` swap per slot.
Run:  python3 gen_art.py <output-dir>
"""
import math
import os
import re
import random
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/img"
os.makedirs(OUT, exist_ok=True)

# --- brand palette -----------------------------------------------------------
INK     = "#0F1E2E"
INK_2   = "#1B3executed"  # placeholder, replaced below
INK_2   = "#1B3348"
CREAM   = "#FAF6EF"
SAND    = "#EADFCB"
CORAL   = "#D2452F"
CORAL_D = "#A8331F"
TEAL    = "#0E7C7B"
TEAL_D  = "#0A5B5A"
GOLD    = "#E0A045"

# Background duotone pairs used to keep the plate set varied but cohesive.
SCHEMES = [
    (INK,   INK_2,   CREAM,  CORAL),
    (TEAL_D, TEAL,   CREAM,  GOLD),
    (SAND,  "#D8C7A9", INK,   CORAL),
    (CORAL_D, CORAL, CREAM,  GOLD),
    (INK_2, "#2A4A66", CREAM, TEAL),
    ("#E7D9C2", SAND, INK,    TEAL),
]

# --- silhouette geometry (authored in a 100x100 box, facing right) -----------
DOG_HEAD = (
    "M18 93 C13 80 12 66 21 47 C26 33 40 25 55 27 "
    "C63 28 68 33 70 40 L88 44 C95 46 96 55 89 57 "
    "L75 58 C72 63 69 67 64 70 C55 76 44 78 37 84 "
    "C32 88 29 91 27 95 Z"
)
DOG_EAR = (
    "M28 36 C17 39 9 53 11 69 C12 78 21 82 27 76 "
    "C32 71 32 52 28 36 Z"
)
DOG_SIT = (
    "M34 96 C30 84 29 72 32 61 C25 57 21 48 23 39 "
    "C25 27 36 20 48 22 C55 23 60 27 63 33 L78 36 "
    "C84 37 85 44 79 46 L68 47 C67 52 64 56 60 59 "
    "C64 66 70 74 74 84 C76 89 77 93 77 96 L66 96 "
    "C65 88 61 79 56 72 C54 80 54 89 55 96 Z"
)
PAW = (
    "M50 84 C38 84 28 77 28 68 C28 60 37 55 50 55 "
    "C63 55 72 60 72 68 C72 77 62 84 50 84 Z "
    "M25 48 m-9,0 a9,10 0 1,0 18,0 a9,10 0 1,0 -18,0 Z "
    "M45 40 m-9,0 a9,11 0 1,0 18,0 a9,11 0 1,0 -18,0 Z "
    "M68 44 m-9,0 a9,10 0 1,0 18,0 a9,10 0 1,0 -18,0 Z "
    "M86 58 m-8,0 a8,9 0 1,0 16,0 a8,9 0 1,0 -16,0 Z"
)

def scissors(stroke, w=5):
    """Grooming shears, authored in a 100x100 box."""
    return f'''<g fill="none" stroke="{stroke}" stroke-width="{w}"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 14 L66 62"/><path d="M78 14 L34 62"/>
      <circle cx="26" cy="76" r="12"/><circle cx="74" cy="76" r="12"/>
      <path d="M34 68 L50 52 L66 68"/>
    </g>'''

def comb(stroke, w=5):
    return f'''<g fill="none" stroke="{stroke}" stroke-width="{w}"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M16 34 H84 a6 6 0 0 1 6 6 v6 H10 v-6 a6 6 0 0 1 6-6 Z"/>
      <path d="M20 52 V80 M32 52 V84 M44 52 V80 M56 52 V84 M68 52 V80 M80 52 V84"/>
    </g>'''

def droplet(stroke, w=5):
    return f'''<g fill="none" stroke="{stroke}" stroke-width="{w}"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M50 12 C50 12 22 44 22 62 a28 28 0 0 0 56 0 C78 44 50 12 50 12 Z"/>
      <path d="M38 62 a12 12 0 0 0 12 12"/>
    </g>'''

def bone(stroke, w=5):
    return f'''<g fill="none" stroke="{stroke}" stroke-width="{w}"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M30 40 h40"/><path d="M30 60 h40"/>
      <circle cx="22" cy="38" r="11"/><circle cx="22" cy="60" r="11"/>
      <circle cx="78" cy="38" r="11"/><circle cx="78" cy="60" r="11"/>
    </g>'''

def house(stroke, w=5):
    return f'''<g fill="none" stroke="{stroke}" stroke-width="{w}"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 50 L50 18 L86 50"/>
      <path d="M24 46 V84 h52 V46"/>
      <path d="M40 84 V62 a10 10 0 0 1 20 0 v22"/>
    </g>'''

def sparkle(stroke, w=5):
    return f'''<g fill="none" stroke="{stroke}" stroke-width="{w}"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M50 14 C54 38 62 46 86 50 C62 54 54 62 50 86 C46 62 38 54 14 50 C38 46 46 38 50 14 Z"/>
    </g>'''

ICONS = {"scissors": scissors, "comb": comb, "droplet": droplet,
         "bone": bone, "house": house, "sparkle": sparkle}


def grain(seed, w, h, ink, count=140, op=0.05):
    """Deterministic speckle so flat fills read as printed stock, not vector."""
    rnd = random.Random(seed)
    dots = []
    for _ in range(count):
        x = round(rnd.uniform(0, w), 1)
        y = round(rnd.uniform(0, h), 1)
        r = round(rnd.uniform(0.6, 2.4), 1)
        dots.append(f'<circle cx="{x}" cy="{y}" r="{r}"/>')
    return f'<g fill="{ink}" opacity="{op}">{"".join(dots)}</g>'


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def head_badge(size, ink, cream, accent):
    """Small brand mark used as a corner badge on every plate."""
    s = size / 100.0
    return f'''<g transform="scale({s:.4f})">
      <path d="{DOG_HEAD}" fill="{cream}"/>
      <path d="{DOG_EAR}" fill="{accent}"/>
      <circle cx="59" cy="41" r="3.6" fill="{ink}"/>
      <circle cx="90" cy="51" r="3.4" fill="{ink}"/>
    </g>'''



def mute(hexcolor, amount=.62, toward=(122, 124, 122)):
    """Blend a brand colour toward neutral grey — used for `before` plates."""
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    tr, tg, tb = toward
    mix = lambda c, t: int(round(c + (t - c) * amount))
    return "#%02X%02X%02X" % (mix(r, tr), mix(g, tg), mix(b, tb))


def plate(name, w, h, scheme_i, subject="head", icon="scissors",
          label=None, seed=None, sweep=True, muted=False):
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

    # Concentric arcs anchored off-canvas give the plate depth.
    ax, ay = w * rnd.uniform(0.06, 0.18), h * rnd.uniform(0.88, 1.02)
    arcs = "".join(
        f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="{m*(0.26+i*0.17):.0f}" '
        f'fill="none" stroke="{fg}" stroke-width="{max(1.0, m*0.0035):.1f}" opacity=".14"/>'
        for i in range(4)
    )

    sweep_svg = ""
    if sweep:
        cx, cy = w * rnd.uniform(0.60, 0.80), h * rnd.uniform(0.16, 0.34)
        rr = m * rnd.uniform(0.44, 0.60)
        sweep_svg = (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rr:.0f}" '
                     f'fill="{fg}" opacity=".09"/>')

    # Hero line-art motif, optically centred and weighted for the plate size.
    icon_fn = ICONS.get(icon, scissors)
    big = m * 0.46
    bx, by = (w - big) * 0.52, (h - big) * 0.44
    bw = 100 * (4.6 / (big / m * 100)) * 0.62

    # Accent chip carrying the brand mark.
    chip = m * 0.165
    cx2, cy2 = w - chip - m * 0.09, m * 0.09

    label_svg = ""
    if label:
        fs = max(11.0, m * 0.052)
        label_svg = (
            f'<path d="M{m*0.09:.0f} {h - m*0.155:.0f} h{m*0.13:.0f}" '
            f'stroke="{accent}" stroke-width="{max(2.0, m*0.011):.1f}" stroke-linecap="round"/>'
            f'<text x="{m*0.09:.0f}" y="{h - m*0.085:.0f}" fill="{fg}" opacity=".85" '
            f'font-family="Inter, Helvetica Neue, Arial, sans-serif" '
            f'font-size="{fs:.0f}" font-weight="600" '
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
      {icon_fn(fg, round(bw, 2))}
    </g>
    <rect x="{cx2 - m*0.042:.0f}" y="{cy2 - m*0.042:.0f}" width="{chip + m*0.084:.0f}" height="{chip + m*0.084:.0f}" rx="{m*0.052:.0f}" fill="{accent}" opacity=".95"/>
    <g transform="translate({cx2:.1f} {cy2:.1f})">{head_badge(chip, a, fg, a)}</g>
    {label_svg}
    {grain(seed, w, h, fg)}
  </g>
</svg>'''


def write(fname, svg):
    with open(os.path.join(OUT, fname), "w") as f:
        f.write(svg)
    return fname


# --- logo --------------------------------------------------------------------
def logo_mark(size=64, ink=INK, accent=CORAL, cream=CREAM):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="Dog Grooming USA mark">
  <rect width="{size}" height="{size}" rx="{size*0.28:.1f}" fill="{ink}"/>
  <g transform="translate({size*0.12:.2f} {size*0.14:.2f}) scale({size*0.0076:.4f})">
    <path d="{DOG_HEAD}" fill="{cream}"/>
    <path d="{DOG_EAR}" fill="{accent}"/>
    <circle cx="59" cy="41" r="3.6" fill="{ink}"/>
    <circle cx="90" cy="51" r="3.4" fill="{ink}"/>
  </g>
  <path d="M{size*0.16:.1f} {size*0.855:.1f} h{size*0.68:.1f}" stroke="{accent}" stroke-width="{size*0.055:.1f}" stroke-linecap="round"/>
</svg>'''

write("logo-mark.svg", logo_mark(64))
write("logo-mark-light.svg", logo_mark(64, ink=CREAM, accent=CORAL, cream=INK))

# Full lockup: mark + wordmark, for the header and footer.
write("logo.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 64" width="300" height="64" role="img" aria-label="Dog Grooming USA">
  <rect width="64" height="64" rx="18" fill="{INK}"/>
  <g transform="translate(7.7 9) scale(0.487)">
    <path d="{DOG_HEAD}" fill="{CREAM}"/>
    <path d="{DOG_EAR}" fill="{CORAL}"/>
    <circle cx="59" cy="41" r="3.6" fill="{INK}"/>
    <circle cx="90" cy="51" r="3.4" fill="{INK}"/>
  </g>
  <path d="M10.2 54.7 h43.5" stroke="{CORAL}" stroke-width="3.5" stroke-linecap="round"/>
  <text x="78" y="30" font-family="Fraunces, Georgia, serif" font-size="23" font-weight="700" fill="{INK}" letter-spacing="-0.3">DOG GROOMING</text>
  <text x="78" y="52" font-family="Inter, Arial, sans-serif" font-size="15" font-weight="700" fill="{CORAL}" letter-spacing="5.6">U S A</text>
</svg>''')

# --- favicon -----------------------------------------------------------------
write("favicon.svg", logo_mark(32))

# --- hero --------------------------------------------------------------------
write("hero.svg", plate("hero", 1000, 760, 0, subject="head",
                        icon="scissors", label="Groomed with care", seed=7))
write("hero-inset.svg", plate("hero-inset", 420, 420, 1, subject="paw",
                              icon="sparkle", seed=11))

# --- services ----------------------------------------------------------------
for i, (f, sub, ic, lb) in enumerate([
    ("svc-grooming.svg", "head", "scissors", "Dog grooming"),
    ("svc-daycare.svg",  "sit",  "bone",     "Dog daycare"),
    ("svc-hotel.svg",    "sit",  "house",    "Dog hotel"),
]):
    write(f, plate(f, 800, 600, i, subject=sub, icon=ic, label=lb, seed=20 + i))

# --- before / after transformations -----------------------------------------
# Each pair shares a scheme, seed and motif so the comparison slider reads as
# one image changing state rather than two unrelated pictures. Labels live in
# the HTML, not the artwork.
TRANSFORMS = [("poodle", 0, "scissors"), ("pomeranian", 1, "comb"), ("yorkie", 4, "sparkle")]
for slug, sch, ic in TRANSFORMS:
    seed = 40 + sch
    write(f"ba-{slug}-before.svg",
          plate(f"ba-{slug}-before", 760, 760, sch, icon=ic, seed=seed, muted=True))
    write(f"ba-{slug}-after.svg",
          plate(f"ba-{slug}-after", 760, 760, sch, icon=ic, seed=seed))

# --- facility ----------------------------------------------------------------
for i, (f, ic, lb) in enumerate([
    ("facility-stations.svg", "scissors", "Grooming stations"),
    ("facility-floor.svg",    "comb",     "Grooming floor"),
    ("facility-play.svg",     "bone",     "Indoor play space"),
    ("facility-finishing.svg","sparkle",  "Detail finishing"),
    ("facility-desk.svg",     "house",    "Front desk"),
]):
    write(f, plate(f, 900, 640, i + 1, icon=ic, seed=60 + i))

# --- gallery -----------------------------------------------------------------
GALLERY = [
    ("gallery-01.svg", "head", "scissors", "Transformation"),
    ("gallery-02.svg", "sit",  "comb",     "In progress"),
    ("gallery-03.svg", "head", "sparkle",  "Finished styling"),
    ("gallery-04.svg", "paw",  "droplet",  "Bath & coat care"),
    ("gallery-05.svg", "sit",  "bone",     "Daycare play"),
    ("gallery-06.svg", "head", "comb",     "Grooming detail"),
    ("gallery-07.svg", "paw",  "sparkle",  "Happy client"),
    ("gallery-08.svg", "sit",  "house",    "Our facility"),
    ("gallery-09.svg", "head", "scissors", "Breed styling"),
]
for i, (f, sub, ic, lb) in enumerate(GALLERY):
    write(f, plate(f, 700, 700, i, subject=sub, icon=ic, label=lb, seed=80 + i))

# --- academy + about ---------------------------------------------------------
write("academy.svg", plate("academy", 900, 700, 3, subject="head",
                           icon="scissors", label="Groomer Artist Academy", seed=101))
write("about.svg", plate("about", 900, 700, 5, subject="sit",
                         icon="droplet", label="Since 2017", seed=102))

# --- open graph card ---------------------------------------------------------
write("og-card.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img" aria-label="Dog Grooming USA">
  <defs><linearGradient id="og" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{INK}"/><stop offset="1" stop-color="{INK_2}"/></linearGradient></defs>
  <rect width="1200" height="630" fill="url(#og)"/>
  <circle cx="1010" cy="180" r="300" fill="{CREAM}" opacity=".07"/>
  <circle cx="120" cy="600" r="150" fill="none" stroke="{CREAM}" stroke-width="2" opacity=".14"/>
  <circle cx="120" cy="600" r="270" fill="none" stroke="{CREAM}" stroke-width="2" opacity=".14"/>
  <circle cx="120" cy="600" r="390" fill="none" stroke="{CREAM}" stroke-width="2" opacity=".14"/>
  <rect x="838" y="188" width="254" height="254" rx="70" fill="{CORAL}"/>
  <g transform="translate(869 219) scale(1.93)">
    <path d="{DOG_HEAD}" fill="{CREAM}"/>
    <path d="{DOG_EAR}" fill="{INK}"/>
    <circle cx="59" cy="41" r="3.6" fill="{INK}"/>
    <circle cx="90" cy="51" r="3.4" fill="{INK}"/>
  </g>
  <text x="86" y="252" font-family="Fraunces, Georgia, serif" font-size="72" font-weight="700" fill="{CREAM}">Dog Grooming USA</text>
  <text x="86" y="316" font-family="Inter, Arial, sans-serif" font-size="33" fill="{SAND}">Trusted dog grooming &amp; pet care</text>
  <text x="86" y="372" font-family="Inter, Arial, sans-serif" font-size="29" fill="{CORAL}" font-weight="600">Serving South Florida since 2017</text>
  <path d="M86 428 h150" stroke="{CORAL}" stroke-width="8" stroke-linecap="round"/>
  <text x="86" y="528" font-family="Inter, Arial, sans-serif" font-size="29" fill="{CREAM}" opacity=".8">305-300-2863  \u00b7  Miami Lakes, FL</text>
</svg>''')

print(f"wrote {len(os.listdir(OUT))} files to {OUT}")
