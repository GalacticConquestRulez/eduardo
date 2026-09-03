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

## What's on the page

Hero · Why us · Services · Before/after comparison sliders · Facility ·
Locations · About · Groomer Artist Academy · Reviews · Gallery with lightbox ·
Appointment form · Franchise CTA · Footer.

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
  inline errors, keyboard-operable comparison sliders and lightbox, and
  `prefers-reduced-motion` support throughout.
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
