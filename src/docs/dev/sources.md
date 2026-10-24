# Sources

A record cites the documents it came from, and those documents are held in
`vogon/sources/` so that the citation can be checked years later. The filing
rules are in `src/vogon/references/sources.md`.

## Location and name

The directory is flat. A document's kind is in its frontmatter, not its
directory, because a record cites a meeting summary and a standard the same
way.

```
vogon/sources/2026-09-17_requirements_workshop.summary.md
vogon/sources/2026-04-02_electronic_records_procedure.pdf
vogon/sources/2026-04-02_electronic_records_procedure.md
```

The date in the name is the document's own, such as the meeting day or the
issue date, so the directory sorts chronologically and two versions differ by
name.

## Original and markdown copy

A document that is not already markdown is held as the original and a
markdown copy. The original is the evidence. The markdown copy can be diffed
and searched, and a reviewer sees in a pull request what a record was written
from. A copy is never corrected by hand, because a hand-edited copy no longer
says what the original says and nothing shows it.

A held document is never changed after filing. A citation asserts that a
specific document says something, and a document edited after the fact cannot
support that.

## Meetings, mail and chat

A meeting, mail thread or chat channel is held only as a reviewed summary. A
transcript holds personal remarks and discussion unrelated to the project,
and the meeting system keeps it under its own retention rule. The downloaded
transcript and messages are therefore kept in the gitignored `vogon/tmp/` and
deleted before the skill commits.

The summary is reviewed against the download before the download is deleted,
because a statement the source did not make cannot be found afterwards. A
requirement drafted from a summary is binding once the requirement approver
approves it; the meeting is only where it came from.

## Authority

`authority` states how strong a document is, from `regulation` to `informal`.
It decides what a record may claim from the document, and a `source` list is
ordered by it. The table of what each value may support is in
`src/vogon/references/sources.md` "Authority".
