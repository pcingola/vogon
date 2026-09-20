# Contributing

## Repository layout

| Path | Contents |
| --- | --- |
| `src/vogon/` | The Python package. The only thing that ships in the wheel. |
| `src/docs/` | Documentation source, markdown. What you are reading. |
| `src/html/` | Marketing page source: `index.html`, `img/`. |
| `docs/` | Build output. Rendered HTML, served by GitHub Pages. Never edit. |
| `gxp/` | VOGON's own records: requirements, facts, constraints, decisions. |
| `tests/` | Test suite. |
| `assets/` | Brand originals. Never published. |

## Development environment

```sh
uv sync
git config core.hooksPath .githooks
make test      # pytest, testpaths = ["tests"]
```

`core.hooksPath` points git at the hooks committed in `.githooks/`. It is a
local setting, so it is set once per clone.

Tests import `vogon` from the installed editable package rather than the
working directory, so a file missing from the wheel fails in CI instead of on a
user's machine.

## Building the site

```sh
make site     # src/docs/ -> docs/, then src/html/ copied over the top
make serve    # live preview on http://127.0.0.1:8000
make clean    # rm -rf docs/
```

`docs/` is generated and committed, because GitHub Pages deploy-from-a-branch
serves exactly what is in git. You do not run `make site` for that: the
`.githooks/pre-commit` hook rebuilds `docs/` and stages it whenever a commit
touches `src/docs/`, `src/html/` or `mkdocs.yml`, so the rendered HTML is
always the render of the source committed beside it. A failing build aborts
the commit.

Do not hand-edit anything inside `docs/`; the next build overwrites it without
asking.

mkdocs and mkdocs-material are pinned in the `dev` dependency group and run
through `uv run --group dev`, so `uv.lock` fixes the renderer version. Do not
call `uvx mkdocs`: it resolves a fresh version each time, and the rendered
output is committed.

## CI

`.github/workflows/ci.yml` runs the tests and a strict site build on every push
and pull request. A broken link or a page missing from the navigation fails the
build, because `mkdocs build --strict` treats warnings as errors.

## Publishing

GitHub Pages, deploy from a branch: Settings → Pages → Source "Deploy from a
branch", branch `main`, folder `/docs`.

```
src/html/index.html            → /
src/html/img/emblem.webp       → /img/emblem.webp
src/docs/user/install.md       → /user/install.html
src/docs/dev/architecture.md   → /dev/architecture.html
assets/                        → not served
```

`src/html/.nojekyll` copies through to `docs/.nojekyll` and stops GitHub
re-running Jekyll over HTML that mkdocs already rendered. mkdocs-material writes
its theme CSS and JS into `docs/assets/`, which is unrelated to the top-level
`assets/`.

## Packaging

```sh
uv build
unzip -l dist/*.whl      # expect vogon/ and vogon-*.dist-info/ only
tar tzf dist/*.tar.gz    # expect src/vogon, tests, README.md, pyproject.toml
```

Three settings in `pyproject.toml` need that output checked after any change:

- `[tool.hatch.version] path = "src/vogon/__init__.py"` — one source of truth
  for the version.
- `[tool.hatch.build.targets.wheel] packages = ["src/vogon"]` — the wheel
  contains `vogon/` and nothing else.
- `[tool.hatch.build.targets.sdist] include = [...]` — hatchling's default is
  everything git tracks, which would ship `assets/` (27 MB) and the generated
  `docs/`. Patterns are anchored with a leading `/`; unanchored `README.md`
  matches at any depth and drags in `assets/README.md`.
