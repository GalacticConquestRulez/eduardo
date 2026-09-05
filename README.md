# Eduardo — proposal landing page

A single-file landing page (`index.html`) that presents Max's proposal to Eduardo: the showcase film, the gallery, the Green Flash raw-footage vault, three boutique films, the offer, the plan, and the September 7 follow-up.

## Hosting

No build step. Every push to `main` runs `.github/workflows/pages.yml`, which publishes the repo root to GitHub Pages. The first run tries to enable Pages automatically; if it is refused, set Settings → Pages → Source to **GitHub Actions** once and re-run the workflow.

Custom domain: point a `CNAME` record at `galacticconquestrulez.github.io` and enter the hostname under Settings → Pages → Custom domain.

## Editing

Every link, name and date lives in `index.html` exactly once. Search for `LINK:` to find each asset link, and `EDIT:` for the package investment lines.

## Background film

`media/` holds the looping background footage, encoded from the Ronin 4D source clip with no audio:

| File | Use | Size |
|------|-----|------|
| `bg-landscape.mp4` | Wide viewports, 1920×804 at 30 fps | ~4.9 MB |
| `bg-portrait.mp4`  | Phones in portrait, 9:16 center crop, 1080×1920 at 30 fps | ~5.6 MB |
| `bg-*.jpg` | Poster frames: instant paint, and the still shown when the viewer prefers reduced motion | |

The page picks the file for the viewport orientation and swaps on rotation. To replace the footage, re-encode with the same names.

## Languages

The top-bar switcher offers English, Spanish, Portuguese and Haitian Creole. English is the HTML itself; the other three live in the `I18N` table at the bottom of `index.html`, keyed by each element's `data-i18n` attribute. Append `?lang=es`, `?lang=pt` or `?lang=ht` to the URL to send a link that opens already translated. The viewer's choice is remembered in their browser.
