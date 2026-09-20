# VOGON

VOGON (Validated Operations & Governance OrchestratioN) is an AI agent for the
bureaucratic side of GxP software development: requirements, validation, risk,
traceability, change control, and audit evidence.

The marketing page, `src/html/index.html`, is written in corporate satire,
defined in `assets/brand.md`. Read that file before editing it. That voice
applies to that page and to nothing else: not the README, not CLI output, not
the documentation, not a record under `gxp/`, not a tracker field VOGON
writes, and not anything VOGON generates in a user's project.

## Writing style

Applies to everything except the marketing page: `CLAUDE.md`, `src/docs/`,
`gxp/`, `README.md`, CLI output, comments, commit messages and working notes,
and everything VOGON generates. The full statement,
including what a checker can enforce, is `src/docs/dev/writing.md`; it is the
same standard, written for the reader rather than for this file. Standard
Technical English: plain declarative sentences, precise terms,
the shortest wording that is still exact.

- A heading names its section. It does not tease it or summarise a conclusion.
- State the fact and let the reader judge its weight. No "critically",
  "importantly", "notably", "it is worth noting", "the key insight".
- No metaphors for importance: nothing is load-bearing, a linchpin, a gate, a
  forcing function or a north star.
- No marketing or management vocabulary, and no coined labels. If a label
  stands in for a plain description, write the plain description.
- No AI slop: no three-item lists built for rhythm, no "not X, but Y", no
  em-dash aside used only for emphasis, no rhetorical question answered by the
  next sentence, no closing line that restates the opening.
- Do not carry vocabulary across from a document you just read. Translate it.

A document states what is settled. Never write a section of open questions,
open issues, TODOs, TBDs or next steps. An unresolved question is raised in
conversation and answered there; if one is already in a file, delete it.

## Repo layout

```
vogon/
├── src/
│   ├── vogon/       CODE — the Python package, the only thing in the wheel
│   ├── docs/        SOURCE — documentation, markdown (user/, dev/)
│   └── html/        SOURCE — marketing page: index.html, img/, .nojekyll
├── docs/            OUTPUT — rendered HTML. generated. never hand-edited.
├── gxp/             RECORDS — VOGON's own requirements, facts, constraints, decisions
├── tests/
├── tmp/             working notes: plans, brainstorming. gitignored, local only.
├── assets/          brand originals + their dark twins, 46 MB. never published.
├── .github/         CI: tests and a strict site build on every push
├── .githooks/       pre-commit: rebuilds docs/ when site source changes
├── mkdocs.yml       docs_dir: src/docs   site_dir: docs
├── Makefile         make site / make clean
└── pyproject.toml
```

`src/` is source and `docs/` is output: never edit `docs/` and never put source
there. Pages serves `main:/docs`, so the rendered HTML is committed, and the
`.githooks/pre-commit` hook rebuilds and stages it whenever a commit touches
the site source. Do not run `make site` by hand before committing. `src/vogon` is the Python package; `src/docs` and `src/html`
are website source that happens to sit beside it, and the wheel is limited to
`src/vogon`. `assets/` is unreachable from the web because Pages roots the site
at `docs/`.

`src/docs/dev/` is the current description of the system. Read
`dev/contributing.md` before changing the build, publishing or packaging,
`dev/site.md` before editing `src/html/index.html`, `dev/architecture.md`
before changing what the system does, and `dev/writing.md` before writing any
prose that ships, including records.

## Records

`gxp/` holds VOGON's own requirements, domain facts, constraints and decisions,
in the same format VOGON defines for the projects it is installed into. Four
kinds of record, four id namespaces, one file per record named for its id, and
an id that is never reused. `src/docs/dev/vocabulary.md` says what the four
words mean, `dev/records.md` says how to write one.

The layout inside `gxp/` is the layout VOGON creates in a host project:
`requirements/<module>/`, `facts/`, `constraints/`, `decisions/`, `sources/`
for held copies of cited documents, and `out/` for generated output. Held
documents are flat and named `YYYY-MM-DD_slug.ext` by the document's own date,
never edited after filing; `dev/sources.md` has the rules. Records
are visible rather than hidden under a dot-directory; `.vogon/` holds tool
state only and is gitignored.

A statement about the system belongs in `gxp/` when it is a requirement, a
fact, a constraint or a decision. It belongs in `src/docs/dev/` when it
explains how the parts fit together. The record says what must hold; the
documentation says how to read the records.

## Version 0.1 assumes one stack

Python, GitHub, Jira, Xray, and Claude Code as the coding agent. Nothing is
abstracted over an alternative, and no interface is written before a second
implementation exists. The reasoning is in `gxp/decisions/DEC-004.md`.

Two consequences hold everywhere. VOGON never performs an approval or a
signature transition, because a signature requires the signer's own
credentials (`gxp/constraints/CON-001.md`). VOGON never calls a language
model: drafting happens in the coding agent, and VOGON validates the result
(`gxp/decisions/DEC-005.md`).

## Plans

A plan states what we are going to build, before the code is written. It is not
a record of what exists. One plan per file, `tmp/plans/plan_<slug>.md`. `tmp/`
is gitignored; nothing committed may depend on a plan.

When a plan has been implemented or abandoned it is spent:
`mv tmp/plans/plan_<slug>.md tmp/plans/done/`. Files under `tmp/plans/done/`
are never read and never updated. Anything that must stay true afterwards goes
to `src/docs/dev/` before the plan is retired.

## Conventions

- Documentation is markdown in `src/docs/`. Rendered HTML is never authored by
  hand and never committed from anywhere but `make site`.
- Directory names don't repeat the project name: `assets/`, not `vogon_assets/`.
