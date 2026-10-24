# Project process files

The process files are `tracking.md`, `requirements.md`, `tests.md`,
`traceability.md`, `documents.md` and `release.md`. Each has a template in
`${CLAUDE_PLUGIN_ROOT}/templates/` that lists its topics and its frontmatter.

## Held plan and outdated files

The held plan is the markdown copy of the validation plan in `vogon/sources/`
(`sources.md`). If several versions are held, the held plan is the one with
the latest document date. A process file is outdated when any of these holds:

- the file has no `plan_source`;
- the held plan is a different file from `plan_source` and has a later
  document date;
- the version the held plan states differs from the file's `plan_version`.

If no validation plan is held, derive the file without one. Skip step 1 and
leave `plan_source` and `plan_version` out of the frontmatter. Every topic of
the template is then a gap that step 5 asks the developer about. When a plan
is filed later, the file is derived again from it.

## Procedure

1. Read the plan version from the plan itself, as its document control or
   title page states it. If the plan states no version, use its document date.
2. For `tracking.md`, ask the developer for one existing tracker item of each
   work type the plan controls. Where `vogon.yaml` names a test manager, also
   ask for one existing test or test procedure item in it. Take the item type names,
   field names, transition names and link names from the items, and ask the
   developer to confirm them.
3. A sub-agent writes the file from the template:
   - the frontmatter: `plan_source`, the path of the held plan's markdown
     copy; `plan_version`, the version from step 1; `derived_on`, the date
     from `date '+%Y-%m-%d'`;
   - each topic of the template as statements, each ending with the plan
     section it rests on, in the form `(plan §<number> <heading>)`, or
     `(plan: <heading>)` where the plan does not number its sections;
   - a tracker or test manager name only as step 2 confirmed it;
   - nothing for a topic the plan does not state. That topic is a gap. The
     sub-agent supplies no default, common practice or value from another
     project for it;
   - when the file is derived again, each answer recorded in step 5 whose
     topic the new plan does not state, with its name and date. An answer
     whose topic the new plan states is dropped.
4. The review checks that each statement says what its cited plan section
   says, and nothing more. A statement with no citation and no recorded
   answer is a finding. A statement that adds a step, approval, field or tool
   the cited section does not state is a finding. A topic the plan states
   that the file leaves out is a finding.
5. Ask the developer each gap: name the topic, quote what the plan states
   nearest to it, and ask how the project does it. The developer may answer
   that the project does not do it. Each answer is recorded under its topic
   in the form
   `Not stated in the plan. Answered by <Name> <email> on <yyyy-mm-dd>: <answer>.`
   The name is the developer's git identity and the date comes from `date`.
6. Commit the file on the skill's branch. Then:
   - If the skill opens a pull request, the file goes in it.
   - If the skill opens no pull request, as with `vogon:next`, push the
     branch and open a pull request for the file.
   - If the skill stops before its pull request, as `vogon:implement` does
     while it waits for a developer's answer to the plan, report the branch.
     The file goes in the pull request of the skill's next run.

   A person merges the pull request.
