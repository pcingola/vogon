# Review (step 4)

Reading the record set as a whole, after step 3 and before the records are
registered: records that contradict or duplicate each other, and statements in
the held documents that no record carries. The review produces a report and,
where the person agrees, edits to `proposed` records. Each item below is a
rule the review meets or fails. The report also follows
`references/writing.md`.

## Scope

- [ ] The review covers every record whose status is `proposed` or
      `accepted`, and every held document in `vogon/sources/` that a record
      cites or that was filed at step 2 for this change.
- [ ] `vogon check` reports no failure before the review starts. A failure
      is fixed first, following `references/records.md`.
- [ ] Records that are `withdrawn` or superseded are read only to find a
      record that still depends on them.

## What the review reports

- [ ] Contradiction: two records that cannot both hold, such as a
      requirement forbidding what another requires, or a requirement that a
      constraint forbids. Both ids are named, with the sentence from each.
- [ ] Duplicate: two records stating the same thing, in the same or other
      words. Both ids are named, and the one that states it more precisely.
- [ ] Overlap: a requirement whose acceptance block tests what another
      requirement's block already tests. Both ids and the clauses are named.
- [ ] Missing record: a sentence of a held document that `records.md`
      classifies as a requirement, fact, constraint or decision, and that no
      record carries. The document path and the sentence are named.
- [ ] Unsupported record: a record whose `source` passage does not say what
      the record says. The id, the path and the passage are named.
- [ ] Stale dependency: a record whose `depends_on` names a record that is
      `withdrawn` or superseded. Both ids are named.
- [ ] Risk level out of line: a requirement whose `gxp_risk` differs from a
      requirement it depends on or duplicates, with no reason in either
      body. Both ids and both levels are named.
- [ ] Each finding is one entry: its kind from this list, the ids or paths,
      and the text that shows it. No finding is a judgement of style that
      `references/writing.md` does not state as a rule.

## What the review does not do

- [ ] It does not change a record's `status`. Moving a record off `proposed`,
      and adding `acceptance_by`, `acceptance_on`, `reviewed_by` and
      `reviewed_on`, are done by the person.
- [ ] It does not edit an `accepted` record. A finding on one goes to the
      person, who decides whether a new record supersedes it.
- [ ] It does not delete a record. A duplicate is set to `withdrawn` or
      `{superseded_by: <id>}` by the person, with the reason in the body.
- [ ] It does not resolve a contradiction by choosing a side. The person
      chooses, and the choice may be a new decision record.
- [ ] It does not assign risk levels. `references/risk.md` covers the risk
      assessment.

## Report

- [ ] The report is given to the person in the conversation, grouped by
      finding kind in the order of the list above.
- [ ] The report is not filed under `vogon/`. What it finds is fixed in the
      records or answered by the person.
- [ ] A review with no finding reports `No findings.` and the scope it read.

## Edits after the report

- [ ] An edit the person agrees to is made to a `proposed` record by
      `vogon-writer`, following `references/records.md`, and checked by
      `vogon-checker`.
- [ ] A missing record is created with `vogon id` and has status `proposed`.
- [ ] `vogon check` reports no failure after the edits.
- [ ] The person is told which records remain `proposed`. Only an `accepted`
      record is registered at step 5.
