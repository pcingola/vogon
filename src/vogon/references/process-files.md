# Project process files

How a skill derives a project process file, `vogon/project/<file>.md`, from the
host project's validation plan, and when it derives the file again.

The process files are `tracking.md`, `requirements.md`, `tests.md`,
`traceability.md`, `documents.md` and `release.md`. Each has a template in
`${CLAUDE_PLUGIN_ROOT}/templates/` that lists its topics and its frontmatter.

## When to derive a file

- The skill needs a process file that does not exist in `vogon/project/`.
  Derive it, then do the skill's task.
- The process file is outdated. Derive it again before acting on it.

The held plan is the markdown copy of the validation plan in `vogon/sources/`
(`${CLAUDE_PLUGIN_ROOT}/references/sources.md`). If several versions are held,
the held plan is the one with the latest document date. A process file is
outdated when any of these holds:

- the file has no `plan_source`;
- the held plan's path differs from the file's `plan_source`, and the held
  plan's date is later;
- the version the held plan states differs from the file's `plan_version`.

If no validation plan is held, derive the file without one. Skip step 1 and
leave `plan_source` and `plan_version` out of the frontmatter. Every topic of
the template is then a gap that step 6 asks the developer about. When a plan
is filed later, the file is derived again from it.

## Procedure

1. Read the plan version from the plan itself, as its document control or
   title page states it. If the plan states no version, use its document date.
2. For `tracking.md`, ask the developer for one existing tracker item of each
   work type the plan controls and, where `vogon.yaml` names a test manager,
   one existing test or test procedure item in it. Read each item through the
   tracker or test manager `vogon.yaml` names. Take the item type names, field
   names, transition names and link names from the items, list them for the
   developer, and ask the developer to confirm them. Give the confirmed names
   to the writing sub-agent.
3. Start a writing sub-agent. Give it the template, the held plan's markdown
   copy, the plan version, the confirmed tracker and test manager names where
   step 2 applies, the output path, its log path and the logs of earlier
   rounds. When the file is derived again, also give it the existing file. The
   writing sub-agent:
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
   - when the file is derived again, keeps each answer recorded in step 6,
     with its name and date, while the new plan does not state its topic. It
     drops an answer whose topic the new plan states.
4. Start two evaluating sub-agents. Give each the file, the template, the
   held plan's markdown copy, its log path and the logs of earlier rounds.
   - Support: each statement says what its cited plan section says, and
     nothing more. A statement with no citation and no recorded answer is a
     finding. A statement that adds a step, approval, field or tool the cited
     section does not state is a finding.
   - Completeness: every topic of the template is covered, by a cited
     statement or by a recorded answer. A topic covered by neither is a gap. A
     plan section that states something about a topic the file leaves out is a
     finding.
5. Run the review loop (`${CLAUDE_PLUGIN_ROOT}/references/loop.md`). The
   writing sub-agent revises the file from the findings.
6. Ask the developer each gap: name the topic, quote what the plan states
   nearest to it, and ask how the project does it. The developer may answer
   that the project does not do it. Give the answers to the writing
   sub-agent, which records each under its topic in the form
   `Not stated in the plan. Answered by <Name> <email> on <yyyy-mm-dd>: <answer>.`
   The name is the developer's git identity and the date comes from `date`.
   Run the evaluators again on the changed file.
7. Commit the file on the skill's working branch
   (`${CLAUDE_PLUGIN_ROOT}/references/common.md` "Working branch"). Then:
   - The skill opens a pull request: the file goes in it.
   - The skill opens no pull request, such as `vogon:next`: push the working
     branch and open a pull request for the file.
   - The skill stops before its pull request, such as `vogon:implement`
     before its tests pass: report the branch. The file goes in the pull
     request of the skill's next run.

   The pull request description states the plan path and version. A person
   merges the pull request.
8. Continue the skill's own task on the same branch, with the file as written
   there.
