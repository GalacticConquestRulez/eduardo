#!/usr/bin/env python3
"""
Bundles the site into one portable HTML file: CSS and JS inlined, every image
and video embedded as a data URI, and the privacy page folded in as a dialog
since a single file has no second page to link to.

Run:  python3 tools/build_single_file.py [output.html]
"""
import base64, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist-single-file.html"

MIME = {".svg": "image/svg+xml", ".png": "image/png", ".webp": "image/webp",
        ".jpg": "image/jpeg", ".mp4": "video/mp4", ".webm": "video/webm"}


def data_uri(rel):
    p = ROOT / rel
    return f"data:{MIME[p.suffix]};base64," + base64.b64encode(p.read_bytes()).decode()


html  = (ROOT / "index.html").read_text()
css   = (ROOT / "assets/css/styles.css").read_text()
js    = (ROOT / "assets/js/main.js").read_text()
legal = (ROOT / "privacy.html").read_text()

body = html.split("<body>", 1)[1].rsplit("</body>", 1)[0]


def collapse(m):
    """<picture> collapses to its WebP source; every viewer here supports it."""
    blk = m.group(0)
    webp = re.search(r'srcset="([^"]+\.webp)"', blk)
    img = re.search(r"<img[^>]*>", blk).group(0)
    return re.sub(r'src="[^"]+"', 'src="%s"' % webp.group(1), img) if webp else img


body = re.sub(r"<picture>.*?</picture>", collapse, body, flags=re.S)

assets = sorted(set(re.findall(r"assets/(?:img|video)/[A-Za-z0-9._-]+", body)))
for a in assets:
    body = body.replace('"%s"' % a, '"%s"' % data_uri(a))

legal_body = legal.split('<div class="wrap legal">', 1)[1].rsplit("</div>", 1)[0]
legal_body = re.sub(r'<p style="margin-top:3em">.*?</p>', "", legal_body, flags=re.S)
legal_css = legal.split("<style>", 1)[1].split("</style>", 1)[0]

body = body.replace('<a href="privacy.html">Privacy Policy</a>',
                    '<a href="#privacy" data-legal>Privacy Policy</a>')
body = body.replace("<!-- Lightbox -->", f'''<div class="legal-modal" id="legalModal" hidden>
  <div class="legal-sheet" role="dialog" aria-modal="true" aria-label="Privacy Policy">
    <button class="legal-close" type="button" aria-label="Close">&times;</button>
    <div class="legal">{legal_body}</div>
  </div>
</div>

<!-- Lightbox -->''')
body = body.replace('<script src="assets/js/main.js" defer></script>\n', "")

EXTRA_CSS = legal_css + """
/* single-file build: privacy dialog */
.legal-modal{position:fixed;inset:0;z-index:130;display:grid;place-items:center;padding:clamp(14px,4vw,44px);background:rgba(6,20,58,.82)}
.legal-modal[hidden]{display:none}
.legal-sheet{position:relative;width:min(760px,100%);max-height:88vh;overflow-y:auto;background:#fff;border-radius:var(--r-lg);padding:clamp(26px,4vw,48px);box-shadow:var(--shadow-lg)}
.legal-sheet .legal h1{font-size:clamp(1.7rem,3.4vw,2.3rem)}
.legal-close{position:sticky;top:0;float:right;width:40px;height:40px;border-radius:50%;border:1px solid var(--line);background:var(--cream);color:var(--ink);font-size:1.5rem;line-height:1;cursor:pointer}
.legal-close:hover{background:var(--ink);color:#fff}
"""

EXTRA_JS = """
  /* single-file build: privacy dialog */
  var legal = document.getElementById('legalModal');
  if (legal) {
    var openLegal = function (e) {
      e.preventDefault(); legal.hidden = false;
      document.body.classList.add('nav-open');
      legal.querySelector('.legal-close').focus();
    };
    var closeLegal = function () { legal.hidden = true; document.body.classList.remove('nav-open'); };
    Array.prototype.forEach.call(document.querySelectorAll('[data-legal]'),
      function (a) { a.addEventListener('click', openLegal); });
    legal.querySelector('.legal-close').addEventListener('click', closeLegal);
    legal.addEventListener('click', function (e) { if (e.target === legal) closeLegal(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !legal.hidden) closeLegal(); });
  }
"""

js = js.rstrip()
assert js.endswith("})();"), "main.js IIFE shape changed; the build needs updating"
js = js[: -len("})();")] + EXTRA_JS + "})();"

OUT.write_text(f"""<title>Dog Grooming USA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{css}
{EXTRA_CSS}
</style>
<script>
  /* Arm scroll-reveal before first paint; without JS the content stays visible. */
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window)
    document.documentElement.classList.add('anim');
</script>
{body}
<script>
{js}
</script>
""")

leftover = re.findall(r'(?:src|href)="(?!#|https://fonts|https://www\.google|data:|tel:|mailto:)[^"]+"', OUT.read_text())
assert not leftover, "unresolved external references: %s" % leftover
print(f"{OUT}: {len(assets)} assets inlined, {OUT.stat().st_size/1024/1024:.2f} MB")
