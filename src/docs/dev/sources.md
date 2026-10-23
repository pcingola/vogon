# Sources

A record cites the documents it came from, and those documents are held in the
repository so the citation can be checked years later. The filing rules a
writing sub-agent and an evaluator apply are in
`src/vogon/references/sources.md`. What a
citation means is in [Records](records.md).

## Location and name

Every held document lives in `vogon/sources/`, flat. Its kind is in its
frontmatter, not its directory, because a record cites a meeting summary and a
standard the same way.

```
vogon/sources/2026-09-17_requirements_workshop.summary.md
vogon/sources/2026-04-02_electronic_records_procedure.pdf
vogon/sources/2026-04-02_electronic_records_procedure.md
```

The date is the document's own (meeting day, issue date), not the filing date,
so the directory sorts chronologically and two versions differ by name.

## Original and markdown copy

A document that is not already markdown is held twice: the original as
received, and a markdown copy beside it with the same stem. The original is
the evidence. The markdown copy diffs and greps, and a reviewer sees in a pull
request what a record was written from. Records cite the markdown copy.

A copy is never corrected by hand. A wrong copy is replaced by a better
conversion, because a hand-edited copy no longer says what the original says
and nothing shows it.

## Edits

A held document is never changed, typos included. A corrected or reissued
document is a new file with its own date. Records citing the old file keep
citing it or are updated deliberately. A citation asserts that a specific
document says something, and a document edited after the fact cannot support
that.

## Meetings, mail and chat

A meeting, mail thread or chat channel is held only as a checked summary,
and the download is deleted before the skill commits
(`src/vogon/references/sources.md`, "Meetings, mail and chat"). A transcript
holds personal remarks and discussion unrelated to the project, some countries
restrict keeping it, and the meeting system keeps it under its own retention
rule.

The summary is checked against the download before the download is deleted,
because a statement the source did not make cannot be found afterwards.
Records are drafted from the checked summary. A requirement drafted from a
summary is binding once the Product Owner approves it; the meeting is only
where it came from.

## Attached and shared files

A file attached to a mail, posted in a chat, shared in a meeting or named by
the developer is filed as its original and markdown copy, and kept. Its date
is the file's own date.

## `authority`

`authority` is `regulation`, `standard`, `procedure`, `project` or `informal`,
strongest first. It decides what a record may claim from the document, and a
`source` list is ordered by it. The table of what each value may support is in
`src/vogon/references/sources.md`. An `informal` document is never the only
support for a domain fact.

## Not held

Documentation the project wrote about itself is not held: it lives in the
project's documentation, and a record points at it with `references`. A document that
cannot be redistributed, such as a licensed standard, is cited by identifier
and clause.
