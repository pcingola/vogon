# Marketing page

`src/html/index.html` is standalone: no build step, copied verbatim into
`docs/` by `make site`. It reads as an enterprise life-sciences SaaS page that
is also a controlled document — a persistent document-control strip, SOP clause
numbering (§1.0 …), square-cornered hairline panels, and one animation: the
REJECTED stamp that lands when a change request is submitted.

## Type and color

Archivo for display, Source Sans 3 for body, IBM Plex Mono for document
metadata and CLI, Source Serif 4 italic for quotes.

Color tokens are sampled from the artwork: paper `#FBFAF5`, ink `#101820`,
oxblood `#971A1C`, stamp `#BF100F`, slate `#6E7B82`, rule `#DFDACF`. Light and
dark are both defined on `:root`. Fixed dark chrome (nav strip, footer, consent
bar) uses the `--dark-ground*` tokens and stays dark in both themes.

## Images

Images are WebP in `src/html/img/` (54 MB of PNG reduced to 2.2 MB), referenced
relatively as `img/…` so the paths survive the copy into `docs/`. Regenerate
with ImageMagick from `assets/images/` after adding artwork.

Most of the artwork was drawn on white paper, which glares on a dark page, so
those figures have a dark twin: `assets/images/<name>_dark.png` is the original
and `src/html/img/<name>_dark.webp` the web copy. Images 01–09, 12 and 13 have
one. The twins were redrawn for dark ground. Flood fills and lightness
inversions were tried and rejected; regenerate the artwork instead.

A dark twin must be the same pixel size as the light `.webp` beside it, because
`index.html` carries one `width`/`height` pair for both sources:

```sh
magick identify -format '%wx%h' src/html/img/<name>.webp
magick assets/images/<name>_dark.png -resize '<W>x<H>!' \
  -quality 82 -define webp:method=6 src/html/img/<name>_dark.webp
```

Where the aspect ratios differ — 04 is square in dark and 1200×1006 in light —
centre-crop to the light ratio first (`-gravity center -crop 1254x1051+0+0
+repage`) rather than squashing.

`emblem.webp` (03) and `stamp-alpha.webp` (08) are transparent cutouts and both
are white-keyed: the vogon's white shirt and the paper inside the stamp frame
went with the background. That reads correctly on cream and leaves holes on
dark ground. Their dark counterparts come off the authored dark artwork
instead — `emblem_dark.webp` is a circular mask of `03-vogon-icon_dark.png`,
and `stamp-alpha_dark.webp` takes its alpha from the brightest channel of
`08-rejected-stamp_dark.png`. The footer stamp uses the dark one
unconditionally because the footer is `--dark-ground` in both themes. The
rejection dialog keeps `stamp-alpha.webp`, which is the stronger red on its
cream card.

A figure with a dark twin is served through `<picture>` with
`media="(prefers-color-scheme: dark)"`, in `index.html` and in the README.
There is no theme toggle, so the media query is the only mechanism.

## Lightbox

Every figure is click-to-enlarge. Wrap it in `<div class="zoomfig"
role="button" tabindex="0">` and the lightbox picks it up, captioned from the
image's `data-ref`. The footer REJECTED stamp is one of these.

The lightbox fits a figure whole and never enlarges it past its own pixels, so
a 1200px figure stops at 1200px on a wide monitor instead of going soft.
Portrait figures are the exception: VGN-PROC-001 is a tall chart containing
body text, and fitted to the dialog height it is unreadable. A figure taller
than it is wide is sized to the dialog width instead, capped at 1.5× its own
pixels, and the area scrolls. Clicking the figure does not close the dialog;
only the backdrop does.
