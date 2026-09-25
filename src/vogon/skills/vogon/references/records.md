# Records (step 3)

Drafting requirements, domain facts, constraints and decisions from held
documents in `vogon/sources/`. Every record also follows
`references/writing.md`. Each item below is a rule the record meets or fails.

## Classifying a sentence

Apply to each sentence of the source, in this order. The first match wins.

1. A test could be written that the system fails: **requirement**.
2. True whether or not anything is built: **domain fact**.
3. A limit imposed from outside that cannot be traded away: **constraint**.
4. Chosen among options, including a choice not to build: **decision**.
5. Nobody knows the answer yet: ask the person. It is not a record.
6. Only what somebody said: it stays in the summary. It is not a record.

- [ ] A sentence stating two of these is split into two records that link to
      each other through `depends_on`.
- [ ] Records are drafted from the transcript or the document, never from a
      summary.

## Files and ids

- [ ] The file was created by `vogon id <TYPE> --module <M> --title <T>`,
      never by choosing a number.
- [ ] An id is `<TYPE>-<NUMBER>` or `<TYPE>-<MODULE>-<NUMBER>`. `TYPE` is
      `REQ`, `FACT`, `CON` or `DEC`. `MODULE` is uppercase letters and digits
      and is listed in `vogon/modules.yaml`.
- [ ] The file is named for the id alone and sits at
      `requirements/<MODULE>/`, `facts/`, `constraints/` or `decisions/`.
- [ ] An id is never reused or renumbered. A record is never deleted: it is
      set to `withdrawn`, with the reason in the body, or to
      `{superseded_by: <id>}`.
- [ ] An accepted decision is never edited. A new decision supersedes it.

## Frontmatter of every record

- [ ] `id`, `type` (`requirement`, `fact`, `constraint`, `decision`),
      `title` and `status` are present.
- [ ] `title` is one line naming what the record is, in the words someone
      would search for. Not a question, not an allusion.
- [ ] `modules` lists every module the record belongs to, and includes the
      module in the id.
- [ ] `status` is `proposed` on every drafted record. The person changes it.
- [ ] `source` lists every held document that states it, by path, strongest
      `authority` first: `regulation`, `standard`, `procedure`, `project`,
      `informal`. A transcript comes before its summary; a summary never
      replaces it. The paths are the markdown files, not the originals.
- [ ] Each document in `source` was read at the passage, not listed for its
      title. Where documents disagree, both are listed and the body states
      the difference. Where only a meeting supports a claim, the body says so.
- [ ] A record the project originated itself has no `source`.
- [ ] `depends_on` lists the records this one rests on, by id. A fact has none.
- [ ] `references` lists the documents, by path from the repository root,
      that say how the record is realised. Absent where none does.
- [ ] `tags` is optional and free-form.
- [ ] `reviewed_by`, `reviewed_on` and `tracked_as` are absent. A person adds
      the first two; `vogon push --record` adds the third.
- [ ] No frontmatter key and no body line states that the record was
      approved or signed.
- [ ] An absent field is absent. No `N/A`, `TBD`, `TODO`, `none considered`,
      `-`, `null`, empty string or empty list. `none` only in `gxp_risk`.

## Body of every record

- [ ] Starts with `# <id> — <title>`.
- [ ] Has at most the word limit: requirement 300, fact 200, constraint 200,
      decision 600. A record over it is split.
- [ ] Every domain term is explained in a clause at first use or linked by id
      to the record that explains it.
- [ ] The example, where there is one, is marked `**Example.**`, is concrete,
      and is illustration. A record with no example has no example block.

## Requirement

- [ ] `verification` is `inspection`, `analysis`, `demonstration` or `test`.
- [ ] `gxp_risk` is `safety`, `product quality`, `data integrity` or `none`:
      what a failure would damage.
- [ ] `**Requirement.**` is one sentence using MUST or MUST NOT, saying what
      has to be true and not how, with no rationale in it. A test can fail it.
- [ ] A short paragraph says what it means and what it does not cover.
- [ ] `**What this does not require.**` states the boundary.
- [ ] `**Acceptance.**` states properties that hold for any project using the
      system, never facts about files on one machine.
- [ ] Every expected value in the acceptance block is stated as a value and
      is worked out from the requirement, never from running the code.
- [ ] `acceptance_by` and `acceptance_on` are absent. A person accepts the
      acceptance block and adds them.
- [ ] A requirement with `gxp_risk` other than `none`, or `verification:
      test`, has an acceptance block.

## Domain fact

- [ ] Plain present tense, no modal verb, no acceptance block.
- [ ] `as_of` is the date it was observed or read.
- [ ] Its `source` names at least one document above `informal`.

## Constraint

- [ ] The body says what it forbids or forces.
- [ ] `imposed_by` names the regulation, numbered procedure, standard or
      platform behaviour. It is not a path.
- [ ] `lifts_when` is the condition under which it stops applying, or
      `permanent`.

## Decision

- [ ] The body has `**Context.**`, `**Options.**` with what each costs,
      `**Decision.**`, `**Consequences.**` including those accepted as bad,
      and `**Example.**`.
- [ ] It states the choice, not the mechanism.

## Done

- [ ] `vogon check` reports no error for the files written.
