# Eduardo — proposal landing page

A single-file landing page (`index.html`) that presents Max's proposal to Eduardo: the showcase film, the gallery, the Green Flash raw-footage vault, three boutique films, the offer, the plan, and the September 7 follow-up.

## Hosting

No build step. Enable GitHub Pages on this branch (Settings → Pages → deploy from branch, root) or drop `index.html` on any static host.

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
