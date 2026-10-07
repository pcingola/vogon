# Sources

A record cites the documents it came from, and those documents are held in the
repository so the citation can be checked years later. This is where they go
and how they are named. What the citation itself means is in
[Records](records.md).

## One directory, flat, dated

Every held document lives in `vogon/sources/`, with no subdirectories. A
meeting summary, a slide deck, a regulation and a file attached to a mail sit
side by side, and
what kind of thing each one is comes from its frontmatter rather than from its
directory. A meeting summary is not filed differently from a standard because
a record cites both the same way.

The filename is the document's date, then a slug:

```
vogon/sources/2026-09-17_requirements_workshop.summary.md
vogon/sources/2026-04-02_electronic_records_procedure.pdf
```

The date is the document's own, such as the day the meeting happened or the
procedure was issued, not the day it was filed. It sorts the directory
chronologically, which is the order anyone looks for something in, and it
makes two versions of the same document distinguishable without reading
either.

The slug is lowercase, words separated by underscores, and describes the
document rather than the record it supports.

## An original and its text

A document that is not already text is held twice: the original as it was
received, and a markdown conversion beside it with the same stem.

```
vogon/sources/2026-04-02_electronic_records_procedure.pdf
vogon/sources/2026-04-02_electronic_records_procedure.md
```

The original is the evidence. The markdown is what people and tools read: it
diffs, it greps, and a reviewer can see in a pull request what a record was
written from. Records cite the markdown.

A conversion is never corrected by hand. If it is wrong, the fix is a better
conversion, because a hand-edited copy no longer says what the original says
and nothing indicates that.

## Frontmatter

Every markdown document in `vogon/sources/` carries frontmatter. The original
binary carries none, which is why the conversion exists.

| Field | Rule |
| --- | --- |
| `title` | The document's own title, as it appears on it |
| `date` | The document's date, matching the filename prefix |
| `kind` | `summary`, `plan`, `procedure`, `standard`, `regulation`, `deck`, `note` or `document` for any other file |
| `authority` | `regulation`, `standard`, `procedure`, `project` or `informal`. What weight a record may give it. See [below](#authority-decides-what-a-record-may-claim) |
| `original` | The file this was converted from, where one exists |
| `participants` | On a summary: who was present at the meeting, as the meeting system lists them, or who wrote the mail or chat messages summarised |
| `retrieved_from` | Where it came from: the system and the item's id in it, such as the meeting's id in the meeting system, or a URL |

## A held document is never edited

Once a document is in `vogon/sources/` its content does not change. A corrected
summary, a reissued procedure, a second version of a deck: each is a new
file with its own date, and the records that cited the old one either keep
citing it or are updated deliberately.

A copy is held because a citation asserts that a specific document says
something, and a document that can be edited after the fact cannot support
that.

Typos are not an exception.

## Meetings, mail and chat

A meeting, a mail thread or a chat channel is held as one document: a summary,
with `kind: summary`, `authority: informal`, its `participants`, and in
`retrieved_from` the system and the meeting's, thread's or channel's id in it.
Its date is the meeting's date, or for a thread or channel the date of the
latest message summarised.

```
vogon/sources/2026-09-17_requirements_workshop.summary.md
```

The recording is not downloaded. The transcript, the mail and the chat
messages are downloaded to `vogon/tmp/`, which is gitignored, and never
committed. A summary is written from them and checked against them, and they
are deleted once the summary is checked. A
transcript holds personal remarks and discussion unrelated to the project,
some countries restrict keeping it, and the meeting system keeps it under its
own retention rule. The summary keeps every requirement, fact, constraint,
decision and unanswered question the source stated, with the values given and
who stated each.

A summary that says something the source did not is a defect in the summary,
and the check against the source exists to find it before the source is
deleted. Records are drafted from the checked summary. A requirement drafted
from a summary becomes binding through the Product Owner's approval, not
through the meeting.

## Attached and shared files

A file attached to a mail, posted in a chat or shared in a meeting is
downloaded and filed in `vogon/sources/` as the original and its markdown copy,
as [above](#an-original-and-its-text), and kept. Its date is the file's own
date, and `retrieved_from` names the system and the message or meeting it came
from. Records cite the markdown copy.

## `authority` decides what a record may claim

Documents differ in what they can support, and the difference is not a matter
of how confident the author sounded.

| `authority` | What it is | What a record may do with it |
| --- | --- | --- |
| `regulation` | A law or a regulator's binding requirement | Support a constraint. Cannot be traded away |
| `standard` | A published standard or industry guide | Support a constraint or a requirement, and be argued with on the record |
| `procedure` | A controlled procedure of the organisation | Support a constraint or a requirement |
| `project` | A document produced by this project or a neighbouring one | Support a requirement or a decision |
| `informal` | A summary of a meeting, mail or chat, or a deck someone wrote | Support a requirement. Never the only support for a domain fact |

A `source` list is ordered by this column, strongest first. A domain fact whose
only source is `informal` is either badly sourced or not a fact, as
[Records](records.md) states.

## What does not go here

Documents the project produced about itself. The architecture, the record
format, this page: those are documentation, they live in `src/docs/`, and a
record points at them with `references` rather than `source`.

Anything that cannot be redistributed with the repository. A licensed standard
is cited by its identifier and its clause, not by a copy of its text.
