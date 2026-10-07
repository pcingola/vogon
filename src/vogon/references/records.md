# Records

Rules for writing and evaluating requirements, domain facts, constraints,
decisions and test procedures in `vogon/`. A writing sub-agent applies them to
what it drafts; an evaluating sub-agent reports each item a record fails.
Every record also follows `references/writing.md`.

## Classifying a sentence

Apply to each statement of a checked summary, a held document or the code, in
this order. The first match wins.

1. A test could be written that the system fails: **requirement**.
2. True whether or not anything is built: **domain fact**.
3. A limit imposed from outside that cannot be traded away: **constraint**.
4. Chosen among options, including a choice not to build: **decision**.
5. Nobody knows the answer yet: a question for the developer. It is not a
   record.
6. Only what somebody said: it stays in the summary. It is not a record.

- [ ] A statement that is two kinds of record is written as two records. The
      one that rests on the other names it in `depends_on`.
- [ ] A statement made in two sources is one record citing both.
- [ ] Records are drafted from checked summaries, markdown copies of held
      documents and the code, never from a downloaded transcript, mail or
      chat.

## Files and ids

- [ ] The id comes from `vogon id <type> <module>`, never from choosing a
      number. The module is omitted for `FACT`, `CON` and `DEC`, and in a
      project without modules.
- [ ] An id is `<TYPE>-<NUMBER>` or `<TYPE>-<MODULE>-<NUMBER>`. `TYPE` is
      `REQ`, `FACT`, `CON`, `DEC` or `TP`. `MODULE` is uppercase letters and
      digits and is a module listed in `vogon/project/vogon.yaml`.
- [ ] The file is named for the id alone and sits at
      `vogon/requirements/<module>/` (requirements and test procedures),
      `vogon/facts/`, `vogon/constraints/` or `vogon/decisions/`.
- [ ] An id is never reused or renumbered, also after withdrawal. A record is
      never deleted: it is set to `withdrawn` or to `{superseded_by: <id>}`.
- [ ] A withdrawn record states the reason for the withdrawal in its body.
- [ ] A merged decision is never edited. A later decision supersedes it, and
      both files stay.

## Frontmatter of every record

- [ ] `id`, `type`, `title` and `status` are present. `type` is
      `requirement`, `fact`, `constraint`, `decision` or `test_procedure`.
- [ ] `title` is one line naming what the record is, in the words someone
      would search for. Not a question, not an allusion.
- [ ] `modules` lists every module the record belongs to, including the
      module in the id.
- [ ] `status` is `active`, `withdrawn`, or `{superseded_by: <id>}`. A
      drafted record is `active`. Approval is not a status.
- [ ] `source` lists every held document that states the record, by the path
      of its markdown file in `vogon/sources/`, strongest `authority` first:
      `regulation`, `standard`, `procedure`, `project`, `informal`. The
      authority table in `references/sources.md` says what each may support.
- [ ] Each document in `source` was read at the passage, not listed for its
      title. Where documents disagree, both are listed and the body states
      the difference. Where only a meeting, mail or chat supports a claim, the
      body says so.
- [ ] A record the project originated itself has no `source`.
- [ ] `depends_on` lists the records this one rests on, by id. A fact has
      none.
- [ ] `references` lists the documents, by path from the repository root,
      that say how the record is realised. Absent where none does. Each path
      resolves.
- [ ] `tags` is optional and free-form.
- [ ] `reviewed_by` and `reviewed_on` are absent until a person has read the
      record in detail. A sub-agent does not add them.
- [ ] No frontmatter key and no body line states that the record was
      approved or signed. Approvals are in the requirement's state file.
- [ ] A field or block with nothing to say is absent.

## Body of every record

- [ ] Starts with `# <id>: <title>`.
- [ ] States the statement in one sentence with no rationale in it, then a
      short paragraph saying what it means and what it does not cover.
- [ ] The example, where there is one, is marked `**Example.**`, is concrete,
      and is illustration.
- [ ] Suggested body lengths: requirement 300 words, fact 200, constraint
      200, decision 600. A record well over its length usually states two
      things and is split.

## Requirement

- [ ] `verification` is `inspection`, `analysis`, `demonstration` or `test`.
- [ ] `gxp_impact` is `patient safety`, `product quality`, `data integrity` or
      `none`: what a failure of the requirement would damage.
- [ ] `gxp_impact_reason` says what a failure would damage, and how.
- [ ] `risk` is `high`, `medium` or `low`, from the severity of a failure, its
      probability and how likely it is to be detected.
- [ ] `risk_reason` states the severity, probability and detectability behind
      the value.
- [ ] Where `vogon/project/requirements.md` states another risk method or
      other levels, the risk fields follow it.
- [ ] `**Requirement.**` is one sentence using MUST or MUST NOT, saying what
      has to be true and not how. A test can fail it.
- [ ] `**Out of scope.**` states behaviour a reader might expect that the
      requirement does not require. Absent where there is none.
- [ ] `**Acceptance criteria.**` is present and states what must be tested.
- [ ] Every expected value in the acceptance criteria is stated as a value
      and is worked out from the requirement and its sources, never read off
      a run of the code.

## Domain fact

- [ ] Present tense, no modal verb, no acceptance criteria, no `depends_on`.
- [ ] `as_of` is the date the fact was observed or read.
- [ ] Its `source` names at least one document above `informal`.

## Constraint

- [ ] The body says what it forbids or forces.
- [ ] `imposed_by` names the regulation, numbered procedure, standard or
      platform behaviour that imposes it. It is not a path.
- [ ] `lifts_when` is the condition under which it stops applying, or
      `permanent`.

## Decision

- [ ] The body has `**Context.**`, `**Options.**` with what each costs,
      `**Decision.**`, `**Consequences.**` including the bad ones, and
      `**Example.**` of the decision applied.
- [ ] It states the choice, not the mechanism.

## Test procedure

Only where `vogon/project/tests.md` keeps test procedures in the repository.
Where they are kept in the tracker, the tracker key is the id and no file is
written.

- [ ] At `vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md`, beside the
      requirements it verifies, with its id from `vogon id TP <module>`.
- [ ] `verifies` lists the requirement ids.
- [ ] The body is numbered steps, each with its expected result.
- [ ] Each expected result is worked out from the requirement and its
      sources, never read off a run of the code.
