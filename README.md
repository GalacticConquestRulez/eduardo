# Dog Grooming USA — landing page

Static marketing site for Dog Grooming USA (Miami Lakes / Doral, FL).
No build step, no framework, no dependencies — open `index.html` and it runs.

```
index.html          Landing page
privacy.html        Privacy policy (linked from the footer)
assets/css/         Single stylesheet, design tokens at the top
assets/js/          Vanilla JS: nav, comparison sliders, lightbox, form
assets/img/         Brand artwork (SVG) — see IMAGES.md
tools/gen_art.py    Regenerates the artwork set
```

## Local preview

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## Single-file build

```bash
python3 tools/build_single_file.py          # → dist-single-file.html
```

Inlines the CSS, JS and every image and video as data URIs, and folds the
privacy page in as a dialog, producing one portable HTML file (~4.6 MB) that
runs with no server. The `assets/` tree stays the source of truth; rerun this
after any change you want reflected in the bundle.

## What's on the page

Grooming film · Hero · Why us · Services · Before/after comparison sliders ·
Facility · Locations · About · Groomer Artist Academy · Reviews · Gallery with
lightbox · Appointment form · Franchise CTA · Footer.

The page opens on the film: a full-bleed band directly under the header, with
the hero and its logo immediately below. The footage is revealed through the
heart from the logo mark, then the mask is dropped so the resting state is
unmasked video. It plays muted and pauses whenever it scrolls out of view. Its
headline is a `<p>`, not a heading, so the hero's `h1` remains the document's
first heading. Below 940px the band shows the frame uncropped with the copy
underneath, rather than overlaying an awkward crop. See `IMAGES.md` for the
encoding and a provenance warning about the supplied clip.

## Before it goes live

1. **Photography.** Swap the SVG plates for real photos — every slot is listed
   in [`IMAGES.md`](IMAGES.md) with its aspect ratio and subject.
2. **Logo.** Already in place — it drives the palette, the header lockup, the
   hero, the footer, the favicon and the social card. See `IMAGES.md` if it is
   ever revised.
3. **Wire up the form.** Set `data-endpoint` on `#bookForm` in `index.html` to
   your handler (Formspree, Netlify Forms, HubSpot — anything that accepts a
   JSON `POST`). Until one is set the form validates and then opens the
   visitor's mail client addressed to `info@doggroomingusa.com`, so no enquiry
   is silently dropped.
4. **Set the real domain** in the `canonical`, `og:url`, and `og:image` tags,
   and in the `url`/`image` fields of the JSON-LD block at the bottom of
   `index.html`.
5. **Social card.** Export `assets/img/og-card.svg` to a 1200×630 JPG and point
   `og:image` at it — some platforms will not render an SVG preview.
5. **Reviews.** The "View Reviews" button points at a Google search. Replace it
   with your Google Business Profile review link.
6. **Analytics.** Add your tag before `</head>` if you want one.

## Notes

- **Accessibility.** Skip link, visible focus rings, labelled form fields with
  inline errors, keyboard-operable comparison sliders and lightbox, an outline
  that starts at `h1`, and `prefers-reduced-motion` support throughout.
- **Structure carries meaning.** The "Why Dog Grooming USA?" cards are parallel
  reasons, not steps, so they carry no numbering — a numbered marker there would
  assert a sequence the content does not have.
- **SEO.** Description and Open Graph tags, plus `PetStore` JSON-LD carrying the
  address, hours, phone, service catalogue, and areas served.
- **Brand.** Palette and typography are derived from the logo: navy `#0A2472`,
  royal blue `#0B5BD3`, orange `#F4681B`, green `#0A7A32`. The tokens live at the
  top of `assets/css/styles.css` and are mirrored in `tools/gen_art.py`.
- **Performance.** No framework. The logo is served as WebP (157 KB) with a
  quantised PNG fallback through `<picture>`; everything else is SVG. The only
  third-party request is Google Fonts (Poppins + Inter), and the CSS falls back
  to system sans stacks if it is blocked.
- **Browsers.** Current Chrome, Safari, Firefox, and Edge. The comparison slider
  uses `clip-path` and the focus style uses `:has()`; both degrade harmlessly.
