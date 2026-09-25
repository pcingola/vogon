# Sources (step 2)

Filing the material records are drafted from: transcripts, summaries,
procedures, standards, regulations, decks, emails and notes. Each item below
is a rule the filed documents meet or fail.

## Location and name

- [ ] Every held document is in `vogon/sources/`, with no subdirectories.
- [ ] The filename is `YYYY-MM-DD_slug.ext`. The date is the document's own:
      the meeting date, the issue date. Not the filing date.
- [ ] The slug is lowercase words joined by underscores and describes the
      document, not the record it supports.
- [ ] A document that cannot be redistributed with the repository, such as a
      licensed standard, is not filed. Records cite it by identifier and
      clause.
- [ ] Documentation the project wrote about itself is not filed here.

## Original and conversion

- [ ] A document that is not already markdown is held twice: the original as
      received, and a markdown conversion beside it with the same stem.
- [ ] The conversion is produced by a tool and never corrected by hand. A
      wrong conversion is replaced by a better conversion.

## Frontmatter of each markdown file

- [ ] `title`: the document's own title, as it appears on it.
- [ ] `date`: the document's date, equal to the filename prefix.
- [ ] `kind`: `transcript`, `summary`, `procedure`, `standard`,
      `regulation`, `deck`, `email` or `note`.
- [ ] `authority`: `regulation` (a law or a regulator's binding
      requirement), `standard` (a published standard or industry guide),
      `procedure` (a controlled procedure of the organisation), `project` (a
      document of this or a neighbouring project) or `informal` (a meeting,
      an email, a deck).
- [ ] `original`: the file converted from, where there is one.
- [ ] `derived_from`: on a summary, the document it was produced from.
- [ ] `participants`: on a transcript or its summary, who was present.
- [ ] `retrieved_from`: for a document fetched from elsewhere, the URL or
      system name.
- [ ] No other field, and no placeholder value in place of an absent field.

## A held document is never edited

- [ ] A file already in `vogon/sources/` is not changed, including for a
      typo. A corrected or reissued document is a new file with its own date.
- [ ] Records citing the earlier file keep citing it, or are changed in a
      separate, deliberate edit.

## Meetings

1. The recording is transcribed. The recording itself is not filed.
2. The transcript is filed as `vogon/sources/<meeting date>_<slug>.md` with
   `kind: transcript`, `authority: informal`, the meeting's `date` and its
   `participants`.
3. A summary is produced from the transcript and filed beside it as
   `<meeting date>_<slug>.summary.md`, with `kind: summary`,
   `authority: informal`, `derived_from` naming the transcript, and the
   `participants`.
4. Records are drafted from the transcript, not from the summary.

- [ ] Every sentence of the summary is supported by the transcript. A
      statement the transcript does not make is a defect in the summary.
- [ ] The summary is written to `references/writing.md`, in its own words,
      not the meeting's.

## Done

- [ ] `vogon check` reports no failure for the files filed.
