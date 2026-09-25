# Records

VOGON's own requirements, domain facts, constraints and decisions, in the
format VOGON defines for the host projects it is installed into.

| Path | Holds |
| --- | --- |
| `requirements/<module>/` | Requirement records, one directory per module |
| `facts/` | Every `FACT-` |
| `constraints/` | Every `CON-` |
| `decisions/` | Every `DEC-` |
| `sources/` | Held copies of the documents records cite, flat and dated |
| `modules.yaml` | The module names the records use |
| `out/` | Generated output. Never hand-edited |

Modules are declared in `modules.yaml`: `REC` for the record schema and its
checks, `TRC` for test markers and the link to the test manager, `TRK` for
reading and writing the tracker and the test manager, `GEN` for the drafting
instructions the plugin ships, and `CLI` for the scripts and configuration.

What the four kinds of record mean is in `src/docs/dev/vocabulary.md`. How to
write one is in `src/docs/dev/records.md`. How the documents they cite are
filed is in `src/docs/dev/sources.md`. The prose standard every record follows
is in `src/docs/dev/writing.md`.

Identity is the id in the frontmatter, and the filename is that id. Nothing
depends on which directory a file sits in. An id is permanent: never reused,
never renumbered, and never recycled after withdrawal.
