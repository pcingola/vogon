# Contributing

## Repository layout

| Path | Contents |
| --- | --- |
| `.claude-plugin/` | The marketplace listing. |
| `src/vogon/` | The Claude Code plugin: skills, references, templates. |
| `src/docs/` | Documentation source, markdown. What you are reading. |
| `src/html/` | Marketing page source: `index.html`, `img/`. |
| `docs/` | Build output. Rendered HTML, served by GitHub Pages. Never edit. |
| `vogon/` | VOGON's own records: requirements, facts, constraints, decisions. |
| `tmp/` | Working notes and plans. Gitignored, local only. |
| `assets/` | Brand originals. Never published. |
| `.github/` | CI workflow. |
| `.githooks/` | The pre-commit hook that rebuilds `docs/`. |

## Development environment

```sh
uv sync
git config core.hooksPath .githooks
```

`core.hooksPath` points git at the hooks committed in `.githooks/`. It is a
local setting, so it is set once per clone.

`pyproject.toml` exists for development only: it holds the dev dependency
group.

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

`.github/workflows/ci.yml` runs the tests and a strict site build on pushes to
`main` and on pull requests. A broken link or a page missing from the navigation fails the
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

## The plugin

The repository is a Claude Code plugin marketplace.
`.claude-plugin/marketplace.json` lists one plugin, `vogon`, with source
`./src/vogon`:

```
src/vogon/
├── .claude-plugin/plugin.json   name, version, description
├── references/                  rules shared by the skills
├── templates/                   templates of the host project's process files
└── skills/
    ├── init/                    SKILL.md
    ├── requirements/            SKILL.md, references/
    ├── approve/                 SKILL.md
    ├── next/                    SKILL.md
    ├── tests/                   SKILL.md, references/
    ├── implement/               SKILL.md, references/
    └── release/                 SKILL.md
```

[Architecture](architecture.md) describes the skills.

The version is in `plugin.json` and nowhere else. There is no wheel and no
PyPI release.

Each release is tagged `v<version>`, with the version read from `plugin.json`,
on the commit that sets it: `v0.1.0` for version `0.1.0`.

```sh
claude plugin validate .           # the marketplace listing
claude plugin validate src/vogon   # the plugin manifest
```

To test the plugin as a host project sees it, open Claude Code in a scratch
git repository and run:

```
/plugin marketplace add /path/to/repo --scope project
/plugin install vogon@vogon --scope project
```

Claude Code copies the plugin into its cache at install, keyed by version. A
change in the working tree reaches the scratch repository only after the plugin
is uninstalled and installed again; `/plugin update` does nothing while the
version is unchanged.
