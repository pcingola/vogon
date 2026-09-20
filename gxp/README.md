# Records

VOGON's own requirements, domain facts, constraints and decisions, in the
format VOGON defines for the projects it is installed into.

| Path | Holds |
| --- | --- |
| `requirements/<module>/` | Requirement records, one directory per module |
| `facts/` | Every `FACT-` |
| `constraints/` | Every `CON-` |
| `decisions/` | Every `DEC-` |
| `sources/` | Held copies of the documents records cite, flat and dated |
| `out/` | Generated output. Never hand-edited |

Modules are `REC` for the record schema and its checks, `TRC` for test markers
and the link to Xray, `TRK` for reading and writing Jira and Xray, `GEN` for
the drafting instructions installed into a host project, and `CLI` for the
command line and configuration.

What the four kinds of record mean is in `src/docs/dev/vocabulary.md`. How to
write one is in `src/docs/dev/records.md`. How the documents they cite are
filed is in `src/docs/dev/sources.md`. The prose standard every record follows
is in `src/docs/dev/writing.md`.

Identity is the id in the frontmatter, and the filename is that id. Nothing
depends on which directory a file sits in. An id is permanent: never reused,
never renumbered, and never recycled after withdrawal.
