# VOGON

VOGON (Validated Operations & Governance OrchestratioN) is an AI agent that handles the bureaucratic burden of GxP software development — requirements, validation, risk, traceability, change control, and the evidence needed to survive audits.

Its culture is relentlessly deadpan corporate satire: bureaucracy is sacred, developers are a regrettable implementation detail, every problem can be solved with more process, and good enough is not compliant.

## Tone rules for generated content

- Deadpan. Never wink at the joke, never explain it.
- The voice is institutional, not personal: forms, revisions, procedures, sign-offs.
- Tagline: *Because good enough is not compliant.*
- Banner keywords: COMPLIANCE · TRACEABILITY · RISK MANAGEMENT · A BRIGHTER TOMORROW.
- Recurring lines: "Same problems. More process." · "It depends." · "Per SOP." · "REJECTED."
- Roughly 80% of any public-facing text should read as a legitimate GxP tool; the remaining 20% is where it goes wrong. Lead serious, then deteriorate.
- Assets and copy live in `vogon_assets/`. Reuse them rather than inventing new catchphrases.

## Brand marks

- Icon: `vogon_assets/images/03-vogon-icon.png` — avatars, favicon, bot identity.
- Hero: `vogon_assets/images/02-vogon-rejected-logo.png` — README header, site hero, decks.
- Secondary mark: `vogon_assets/images/08-rejected-stamp.png` — the REJECTED stamp. Use it wherever VOGON says no: PR bot comments, CLI output, error states, CI failures. ASCII reduction for terminals:

```text
        ┌─────────────────┐
        │    REJECTED     │
        │      VOGON      │
        └─────────────────┘
```

## Site

`index.html` at the repo root is the marketing site (standalone, ready for GitHub Pages). It reads as an enterprise life-sciences SaaS page that is secretly a controlled document: a persistent document-control strip, SOP clause numbering (§1.0 …), square-cornered hairline panels, and one animated moment — the REJECTED stamp that lands when a change request is submitted.

- Type: Archivo (display), Source Sans 3 (body), IBM Plex Mono (document metadata, CLI), Source Serif 4 italic (quotes).
- Color tokens are sampled from the artwork: paper `#FBFAF5`, ink `#101820`, oxblood `#971A1C`, stamp `#BF100F`, slate `#6E7B82`, rule `#DFDACF`. Light and dark are both defined on `:root`; fixed dark chrome (nav strip, footer, consent bar) uses the `--dark-ground*` tokens so it stays dark in both themes.
- The site loads web-optimized WebP from `vogon_assets/images/web/` (54 MB of PNG → 2.1 MB). Regenerate with ImageMagick after adding artwork; `emblem.webp` and `stamp-alpha.webp` are transparent cutouts.

## Architecture

<!-- No code yet. -->

## Build & run

<!-- No code yet. -->

## Tests

<!-- No code yet. -->

## Conventions

<!-- No code yet. -->
