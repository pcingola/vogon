# Project process files

How a skill derives a project process file, `vogon/project/<file>.md`, from the
host project's validation plan, and when it derives the file again. The loop
rules, the start-of-skill reads, the systems by role, the actions never taken
and the writing standard are in
`${CLAUDE_PLUGIN_ROOT}/references/common.md`. Read that file first.

The process files are `tracking.md`, `requirements.md`, `tests.md`,
`traceability.md`, `documents.md` and `release.md`. Each has a template in
`${CLAUDE_PLUGIN_ROOT}/templates/` that lists its topics and its frontmatter.
A process file is VOGON's reading of the plan. The plan stays the host
project's controlled document. Never edit the plan or its markdown copy.

## When to derive a file

- The skill needs a process file that does not exist in `vogon/project/`.
  Derive it, then do the skill's task.
- The held plan is newer than the plan the file was derived from. Derive the
  file again before acting on it.

The held plan is the markdown copy of the validation plan in `vogon/sources/`
(`${CLAUDE_PLUGIN_ROOT}/references/sources.md`). If several versions are held,
the held plan is the one with the latest document date. It is newer than a
process file when its path differs from the file's `plan_source` and its date
is later, or when the version it states differs from the file's
`plan_version`.

If no validation plan is held, stop and tell the developer to file it with
`vogon:init`.

## Inputs

- The template, `${CLAUDE_PLUGIN_ROOT}/templates/<file>.md`.
- The held plan, its markdown copy, and the version the plan states on itself.
- `vogon/project/vogon.yaml`, for the system that fills each role.
- When the file is derived again, the existing process file.
- For `tracking.md`, one example item of each work type the plan controls,
  read from the tracker, and, where `vogon.yaml` names a test manager, one
  example test or test procedure item read from the test manager.

## Procedure

1. Read the plan version from the plan itself, as its document control or
   title page states it. If the plan states no version, use its document date.
2. For `tracking.md`, ask the developer for one existing tracker item of each
   work type the plan controls and, where `vogon.yaml` names a test manager,
   one existing test or test procedure item in it. Read each item through the
   system the configuration names for its role. Take the item type names,
   field names, transition names and link names from the items, list them for
   the developer, and ask the developer to confirm them, a stop `common.md`
   lists. Give the confirmed names to the writing sub-agent.
3. Start a writing sub-agent. Give it the template, the held plan's markdown
   copy, the plan version, the confirmed tracker and test manager names where
   step 2 applies, the output path, its log path and the logs of earlier
   rounds. When the file is derived again, also give it the
   existing file. The writing sub-agent:
   - fills the frontmatter: `plan_source`, the path of the held plan's
     markdown copy; `plan_version`, the version from step 1; `derived_on`, the
     date from `date '+%Y-%m-%d'`;
   - writes each topic of the template as statements, each ending with the
     plan section it rests on, in the form `(plan §<number> <heading>)`, or
     `(plan: <heading>)` where the plan does not number its sections;
   - writes a tracker or test manager name only as step 2 confirmed it;
   - writes nothing for a topic the plan does not state, and lists that topic
     as a gap in its log. It does not supply a default, a common practice or a
     value from another project;
   - when the file is derived again, keeps each recorded answer whose topic the
     new plan still does not state, with its name and date, and drops an
     answer the new plan now covers.
4. Start two evaluating sub-agents. Give each the file, the template, the held plan's markdown copy, its log
   path and the logs of earlier rounds.
   - Support: each statement says what its cited plan section says, and
     nothing more. A statement with no citation and no recorded answer is a
     finding. A statement that adds a step, approval, field or tool the cited
     section does not state is a finding.
   - Completeness: every topic of the template is covered, by a cited
     statement or by a recorded answer. A topic covered by neither is a gap. A
     plan section that states something about a topic the file leaves out is a
     finding.
5. Run the loop as `common.md` states, with the writing sub-agent revising
   from the findings.
6. Ask the developer each gap: name the topic, quote what the plan states
   nearest to it, and ask how the project does it. The developer may answer
   that the project does not do it. Give the answers to the writing
   sub-agent, which records each under its topic in the form
   `Not stated in the plan. Answered by <Name> <email> on <yyyy-mm-dd>: <answer>.`
   The name is the developer's git identity and the date comes from `date`.
   Run the evaluators again on the changed file.
7. Commit the file on the skill's working branch, which the skill creates or
   checks out in its first step, before the file is derived. The
   file goes in the skill's one pull request, whose description also states the plan path and version and the
   loops run for the file, their rounds and the findings left open, as
   `common.md` states. A person merges it. If the skill ends without opening
   its own pull request, push the working branch and open a pull request for
   it. A skill that opens its pull request later from the same branch pushes
   to the open one instead.
8. Continue the skill's own task on the same branch, with the file as written
   there.

## Outputs

| Path | Format | Written by |
| --- | --- | --- |
| `vogon/project/<file>.md` | Markdown with YAML frontmatter, in the template's structure | Writing sub-agent |
| `vogon/logs/<yyyymmdd_hhmmss>_<task>.log.md` | Markdown, one per sub-agent run | Each sub-agent |
| `vogon/logs/` main log | One entry per sub-agent run and decision, as `common.md` states | Main agent |
| The skill's pull request on the repository host | The file, with the description from step 7 | Main agent |
