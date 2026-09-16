# Contributing

## Repository layout

| Path | Contents |
| --- | --- |
| `src/vogon/` | The Python package. The only thing that ships in the wheel. |
| `src/docs/` | Documentation source, markdown. What you are reading. |
| `src/html/` | Marketing page source: `index.html`, `img/`. |
| `docs/` | Build output. Rendered HTML, served by GitHub Pages. Never edit. |
| `tests/` | Test suite. |
| `assets/` | Brand originals. Never published. |

## Building the site

```sh
make site     # src/docs/ -> docs/, then src/html/ copied over the top
make serve    # live preview on http://127.0.0.1:8000
make clean    # rm -rf docs/
```

`docs/` is generated and committed, because GitHub Pages deploy-from-a-branch
serves exactly what is in git. Do not hand-edit anything inside it; the next
`make site` will overwrite your changes without asking.

## Development environment

```sh
uv sync
uv run pytest
```
