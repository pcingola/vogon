# Sources

Rules for filing a held document in `vogon/sources/`: a summary of a meeting,
mail thread or chat channel, the validation plan, or a file attached to a
mail, posted in a chat, shared in a meeting or named by the developer. A
writing sub-agent applies them to what it files; an evaluating sub-agent
reports each item a filed document fails. Every summary also follows
`references/writing.md`.

## Location and name

- [ ] Every held document is in `vogon/sources/`, with no subdirectories.
- [ ] The filename is `YYYY-MM-DD_slug.ext`. The date is the document's own,
      such as the meeting date or the issue date, never the filing date. A
      summary of a mail thread or chat channel takes the date of the latest
      message summarised.
- [ ] A summary is named `YYYY-MM-DD_slug.summary.md`.
- [ ] The slug is lowercase words joined by underscores and describes the
      document, not the record it supports.
- [ ] A document that cannot be redistributed with the repository, such as a
      licensed standard, is not filed. Records cite it by identifier and
      clause.
- [ ] Documentation the project wrote about itself is not filed. Records
      point at it with `references`.

## Original and markdown copy

- [ ] A document that is not already markdown is held twice: the original as
      received, and a markdown copy beside it with the same stem.
- [ ] The markdown copy is produced by a tool and never corrected by hand. A
      wrong copy is replaced by a better conversion.
- [ ] Records cite the markdown copy, never the original.

## Frontmatter of each markdown file

- [ ] `title`: the document's own title, as it appears on it.
- [ ] `date`: the document's date, equal to the filename prefix.
- [ ] `kind`: `summary`, `plan`, `procedure`, `standard`, `regulation`,
      `deck`, `note`, or `document` for any other file.
- [ ] `authority`: one of the values in the table below.
- [ ] `original`: the file the markdown copy was converted from, where there
      is one.
- [ ] `participants`: on a summary only. Who was present at the meeting, as
      the meeting system lists them, or who wrote the mail or chat messages
      summarised.
- [ ] `retrieved_from`: the system and the item's id in it, such as the
      meeting's id in the meeting system or the message a file was attached
      to, or a URL.
- [ ] No other field, and no placeholder value in place of an absent field.

## Authority

`authority` decides what a record may claim from the document. A record lists
its `source` documents in the order of this table, strongest first.

| `authority` | What it is | What a record may do with it |
| --- | --- | --- |
| `regulation` | A law or a regulator's binding requirement | Support a constraint. Cannot be traded away |
| `standard` | A published standard or industry guide | Support a constraint or a requirement, and be argued with on the record |
| `procedure` | A controlled procedure of the organisation | Support a constraint or a requirement |
| `project` | A document produced by this project or a neighbouring one | Support a requirement or a decision |
| `informal` | A summary of a meeting, mail or chat, or a deck someone wrote | Support a requirement. Never the only support for a domain fact |

## A held document is never edited

- [ ] A file already in `vogon/sources/` is not changed, including for a
      typo. A corrected or reissued document is a new file with its own date.
- [ ] Records citing the earlier file keep citing it, or are changed in a
      separate, deliberate edit.

## Meetings, mail and chat

- [ ] The transcript, mail and chat messages are downloaded to `vogon/tmp/`,
      which is gitignored. They are never filed in `vogon/sources/` and never
      committed. The recording is not downloaded.
- [ ] Each meeting, mail thread or chat channel is held as one summary, with
      `kind: summary` and `authority: informal`.
- [ ] Every statement of the summary is supported by the downloaded source. A
      statement the source does not make is a defect in the summary.
- [ ] The summary keeps every requirement, fact, constraint, decision and
      unanswered question the source states that bears on requirements, with
      the values given and who stated each.
- [ ] The summary is written in its own words, not the source's.
- [ ] The download is deleted once the summary is checked. Records are drafted
      from the checked summary.

## Attached and shared files

- [ ] A file attached to a mail, posted in a chat, shared in a meeting or
      named by the developer is filed as the original and its markdown copy,
      and kept.
- [ ] Its date is the file's own date.
