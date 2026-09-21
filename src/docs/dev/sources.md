# Sources

A record cites the documents it came from, and those documents are held in the
repository so the citation can be checked years later. This is where they go
and how they are named. What the citation itself means is in
[Records](records.md).

## One directory, flat, dated

Every held document lives in `vogon/sources/`, with no subdirectories. A
transcript, a slide deck, a regulation, an email and a summary sit side by
side, and what kind of thing each one is comes from its frontmatter rather than
from its directory. A meeting transcript is not filed differently from a
standard because a record cites both the same way.

The filename is the document's date, then a slug:

```
vogon/sources/2026-09-17_requirements_workshop.md
vogon/sources/2026-04-02_electronic_records_procedure.pdf
```

The date is the document's own — when the meeting happened, when the procedure
was issued — not when it was filed. It sorts the directory chronologically,
which is the order anyone looks for something in, and it makes two versions of
the same document distinguishable without reading either.

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
| `kind` | `transcript`, `summary`, `procedure`, `standard`, `regulation`, `deck`, `email` or `note` |
| `authority` | `regulation`, `standard`, `procedure`, `project` or `informal`. What weight a record may give it. See [below](#authority-decides-what-a-record-may-claim) |
| `original` | The file this was converted from, where one exists |
| `derived_from` | The document this was produced from, on a summary |
| `participants` | Who was present, on a transcript or a summary of one |
| `retrieved_from` | Where it came from, for a document fetched from elsewhere: a URL, a system name |

## A held document is never edited

Once a document is in `vogon/sources/` its content does not change. A corrected
transcript, a reissued procedure, a second version of a deck: each is a new
file with its own date, and the records that cited the old one either keep
citing it or are updated deliberately.

This is the whole point of holding a copy. A citation asserts that a specific
document says something, and a document that can be edited after the fact
cannot support that.

Typos are not an exception.

## Meetings

A meeting becomes two held documents. The recording is transcribed, and the
transcript is filed with `kind: transcript`, the meeting's date, and the
participants. A summary is produced from that transcript and filed beside it.
Records are drafted from the transcript.

The recording itself is not held. It is large, it is often subject to a
retention rule of its own, and the transcript is what a citation points at.

## Summaries

A transcript is long and nobody reads it twice. A summary of one is held
alongside it, with `kind: summary` and `derived_from` naming the transcript:

```
vogon/sources/2026-09-17_requirements_workshop.md
vogon/sources/2026-09-17_requirements_workshop.summary.md
```

A summary is a convenience, not an authority. Where a record's statement rests
on something said in a meeting, the `source` list names the transcript; the
summary may be listed after it, never instead of it. A summary that says
something the transcript does not is a defect in the summary.

A summary is generated, and generated text is wrong in ways that read well. It
is held so a person can find the passage that matters, and the passage is then
read in the transcript.

## `authority` decides what a record may claim

Documents differ in what they can support, and the difference is not a matter
of how confident the author sounded.

| `authority` | What it is | What a record may do with it |
| --- | --- | --- |
| `regulation` | A law or a regulator's binding requirement | Support a constraint. Cannot be traded away |
| `standard` | A published standard or industry guide | Support a constraint or a requirement, and be argued with on the record |
| `procedure` | A controlled procedure of the organisation | Support a constraint or a requirement |
| `project` | A document produced by this project or a neighbouring one | Support a requirement or a decision |
| `informal` | A meeting, an email, a deck someone wrote | Support a requirement. Never the only support for a domain fact |

A `source` list is ordered by this column, strongest first. A domain fact whose
only source is `informal` is either badly sourced or not a fact, which is the
rule in [Records](records.md) stated in terms a checker can apply.

## What does not go here

Documents the project produced about itself. The architecture, the record
format, this page: those are documentation, they live in `src/docs/`, and a
record points at them with `references` rather than `source`.

Anything that cannot be redistributed with the repository. A licensed standard
is cited by its identifier and its clause, not by a copy of its text.
