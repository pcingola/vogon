# Risk assessment (step 4)

Drafting the risk assessment: for each requirement, its risk level and the
reasoning behind it, for the roles that approve it in the document system
(`REQ-GEN-8`, `DEC-013`). Each item below is a rule the assessment meets or
fails. It also follows `references/writing.md` and `references/documents.md`.

## File

- [ ] The assessment is `vogon/documents/risk_assessment.md`, one file for
      the project. A later assessment replaces the draft in that file.
- [ ] It starts with `# Risk assessment`, then a paragraph naming the commit
      of the records it assessed (`git rev-parse HEAD`) and the date.
- [ ] It defines each level once, before the table, as what a failure would
      damage, in these words: `safety` (harm to a patient or user), `product
      quality` (a product or result that does not meet its specification),
      `data integrity` (regulated data that loses one of the ALCOA+
      properties: attributable, legible, contemporaneous, original,
      accurate, complete, consistent, enduring, available), `none` (none of
      these).

## The table

The scripts parse the table (`snapshots.py`, `parse_risk_assessment`). A table
they cannot parse fails `vogon check` once the approved copy is read back.

- [ ] The document holds one table, and its header row is exactly:

      | Requirement | Risk | Failure would damage | Basis |
      | --- | --- | --- | --- |

- [ ] No other table comes before it whose first columns are `Requirement`
      and `Risk`.
- [ ] One row per requirement whose status is `proposed` or `accepted`,
      including those at `none`. No row for a `withdrawn` or superseded
      requirement, and no requirement appears twice.
- [ ] The rows follow the header with no blank line or other text between
      them. The first line that is not a row ends the table.
- [ ] Column `Requirement` is the record id as the record writes it, such as
      `REQ-API-3`, optionally in backticks, and nothing else.
- [ ] Column `Risk` is exactly one of `safety`, `product quality`, `data
      integrity`, `none`, in lowercase, and equals the requirement's
      `gxp_risk`.
- [ ] Column `Failure would damage` says what a failure of that requirement
      would damage, in terms of the level: whose data, which product, which
      person, in at most two sentences. A failure is the requirement's own
      statement not holding.
- [ ] Every fact about the system, the domain or a regulation that a
      `Failure would damage` cell uses is stated in a record or held
      document that the row's `Basis` cites. The cell adds no behaviour,
      cause or consequence that those inputs do not state.
- [ ] Column `Basis` cites, by id or path, the records, held documents and
      findings that informed the level: the constraints and facts the
      requirement rests on, the held procedure or regulation, and each
      review finding from `references/review.md` that names the requirement
      itself. Every id the row's `Failure would damage` cell names is in
      `Basis`.
- [ ] A row with a level other than `none` has all four columns filled, and
      its `Failure would damage` cell names the damage from that level's
      definition. Where the inputs support no such damage, the cell names
      the level the assessment finds instead, as the next section states. A row at `none` states in `Failure would damage` the
      effect of a failure, taken from the cited inputs, and that this effect
      is none of the damages the level definitions name. It does not argue
      each level separately.
- [ ] No cell contains `|` or a line break. A list inside a cell is separated
      by commas or semicolons.

**Example.**

    | Requirement | Risk | Failure would damage | Basis |
    | --- | --- | --- | --- |
    | REQ-API-3 | data integrity | A result could be stored against the wrong sample | CON-2, FACT-4, vogon/sources/2026-03-02_sample_handling_sop.md |

## The levels and the records

- [ ] The level in the table always equals the record's `gxp_risk`. The
      writer does not change a record's level. Where the assessment finds a
      different level, the row keeps the record's level and the difference
      goes to the person, who changes the record following
      `references/records.md` while it is `proposed`.
- [ ] Such a row's `Failure would damage` cell says what a failure would
      damage, then names the level the assessment finds instead. The
      difference is not a finding against the draft, and the cell need not
      name the damage of the record's level.
- [ ] Each level is worked out from what a failure would damage, never from
      how hard the requirement is to build or test.
- [ ] Where a requirement's `depends_on` names another requirement whose
      level differs, both rows cite the review finding "risk level out of
      line" in `Basis`, and the difference goes to the person. The cells do
      not argue the difference, and requirements not linked by `depends_on`
      are not compared.

## Approval and read-back

- [ ] The assessment is filed and approved in the document system following
      `references/documents.md`, by the roles `approvals.risk_assessment` in
      `vogon.yaml` names.
- [ ] Once approved, the approved version is read back from the document
      system and saved, unchanged, as `.vogon/risk_assessment.md`.
- [ ] `vogon check` then reports no failure for `REQ-GEN-9`. A requirement
      whose level changed after the approval is reported, and the
      assessment is drafted, filed and approved again.
