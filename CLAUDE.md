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
- Assets and copy live in `assets/`. Reuse them rather than inventing new catchphrases.

## Brand marks

- Icon: `assets/images/03-vogon-icon.png` — avatars, favicon, bot identity.
- Hero: `assets/images/02-vogon-rejected-logo.png` — README header, site hero, decks.
- Secondary mark: `assets/images/08-rejected-stamp.png` — the REJECTED stamp. Use it wherever VOGON says no: PR bot comments, CLI output, error states, CI failures. ASCII reduction for terminals:

```text
        ┌─────────────────┐
        │    REJECTED     │
        │      VOGON      │
        └─────────────────┘
```

## Repo layout

```
vogon/
├── src/
│   ├── vogon/       CODE — the Python package, the only thing in the wheel
│   ├── docs/        SOURCE — documentation, markdown (user/, dev/)
│   └── html/        SOURCE — marketing page: index.html, img/, .nojekyll
├── docs/            OUTPUT — rendered HTML. generated. never hand-edited.
├── tests/
├── assets/          brand originals, 27 MB. never published.
├── mkdocs.yml       docs_dir: src/docs   site_dir: docs
├── Makefile         make site / make clean
└── pyproject.toml
```

Three rules hold this together:

1. **`src/` is source, `docs/` is output.** Never edit anything under `docs/`; `make site` overwrites it. Never put source under `docs/`.
2. **`src/` is not the Python import root alone** — `src/vogon` is the package, `src/docs` and `src/html` are website source that happens to live beside it. The wheel is limited to `src/vogon` explicitly (see Build & run), so nothing else ships.
3. **`assets/` is never served.** GitHub Pages roots the site at `docs/`, so anything outside it is unreachable by construction. The 27 MB of full-size PNGs stay for the README and decks.

## Site

`src/html/index.html` is the marketing page — standalone, no build step, copied verbatim into `docs/`. It reads as an enterprise life-sciences SaaS page that is secretly a controlled document: a persistent document-control strip, SOP clause numbering (§1.0 …), square-cornered hairline panels, and one animated moment — the REJECTED stamp that lands when a change request is submitted.

- Type: Archivo (display), Source Sans 3 (body), IBM Plex Mono (document metadata, CLI), Source Serif 4 italic (quotes).
- Color tokens are sampled from the artwork: paper `#FBFAF5`, ink `#101820`, oxblood `#971A1C`, stamp `#BF100F`, slate `#6E7B82`, rule `#DFDACF`. Light and dark are both defined on `:root`; fixed dark chrome (nav strip, footer, consent bar) uses the `--dark-ground*` tokens so it stays dark in both themes.
- Images are web-optimized WebP in `src/html/img/` (54 MB of PNG → 2.2 MB), referenced relatively as `img/…` so the paths survive the copy into `docs/`. Regenerate with ImageMagick from `assets/images/` after adding artwork; `emblem.webp` and `stamp-alpha.webp` are transparent cutouts.

## Publishing

GitHub Pages, deploy-from-a-branch: **Settings → Pages → Source: "Deploy from a branch", branch `main`, folder `/docs`.** No CI workflow. Pages serves `docs/` exactly as committed, which is why build output is committed to git.

```
src/html/index.html            → /
src/html/img/emblem.webp       → /img/emblem.webp
src/docs/user/install.md       → /user/install.html
src/docs/dev/architecture.md   → /dev/architecture.html
assets/                        → not served
```

`src/html/.nojekyll` copies through to `docs/.nojekyll` and stops GitHub re-running Jekyll over HTML that mkdocs has already rendered.

One name collision to be aware of: mkdocs-material writes its own CSS and JS
into `docs/assets/`. That is generated theme output and has nothing to do with
the repo's top-level `assets/`, which holds the brand originals and is never
published.

## Architecture

`src/vogon/` is a stub: `__init__.py` holds `__version__` (hatchling reads the
version from it), `cli.py` provides the `vogon` console-script entry point.

## Build & run

```sh
make site      # src/docs/*.md → docs/, then src/html/ copied over the top
make serve     # live preview on http://127.0.0.1:8000
make clean     # rm -rf docs/
make test      # pytest
uv sync        # dev environment
uv build       # wheel + sdist
```

The docs toolchain (mkdocs + mkdocs-material) is pinned in the `dev`
dependency group and run through `uv run --group dev`, so `uv.lock` fixes the
renderer version. Do not call `uvx mkdocs` — it resolves a fresh version on
every invocation and the rendered output is committed.

Three packaging settings are load-bearing:

- `[tool.hatch.version] path = "src/vogon/__init__.py"` — one source of truth for the version.
- `[tool.hatch.build.targets.wheel] packages = ["src/vogon"]` — the wheel contains `vogon/` and nothing else.
- `[tool.hatch.build.targets.sdist] include = [...]` — hatchling's sdist default is "everything git tracks", which would ship `assets/` (27 MB) and the generated `docs/` to anyone installing from source. Patterns are **anchored with a leading `/`**: unanchored `README.md` matches at any depth and drags in `assets/README.md`.

Verify both after changing packaging config:

```sh
unzip -l dist/*.whl      # expect vogon/ and vogon-*.dist-info/ only
tar tzf dist/*.tar.gz    # expect src/vogon, tests, README.md, pyproject.toml
```

## Tests

```sh
make test
```

`pytest`, `testpaths = ["tests"]`. Tests import `vogon` from the installed
(editable) package, not from the working directory — that is what src-layout
buys, so a file missing from the wheel fails in CI rather than on a user's
machine.

## Conventions

- Documentation is written as markdown in `src/docs/`. Rendered HTML is never authored by hand and never committed from anywhere but `make site`.
- Directory names don't repeat the project name: `assets/`, not `vogon_assets/`; `img/`, not `assets/images/web/`.
