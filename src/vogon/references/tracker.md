# Tracker and test manager (steps 5, 10 and 15)

Registering accepted records as tracker issues (step 5), marked tests as test
issues linked to them (step 10), and the results of a build against the test
issues (step 15). `vogon push --plan` decides every write; Claude Code reads,
shows and applies. Each item below is a rule the step meets or fails.

## Before reading

- [ ] The step reads and writes only through the servers `vogon.yaml` names
      for `tracker` and `test_manager`. A role with no server is reported as
      not configured and its part of the step is skipped.
- [ ] `vogon check` reports no error.
- [ ] Step 5 registers only `accepted` records. Step 10 follows the step 10
      items of `references/tests.md`. Step 15 needs `vogon trace` run on a
      committed working tree, so `.vogon/results.json` records a build.

## Reading into `.vogon/tracker.json`

The format is in the docstring of `${CLAUDE_PLUGIN_ROOT}/scripts/snapshots.py`.
Read it before writing the file.

- [ ] `read_at` is the time of the read, ISO 8601 with a UTC offset.
- [ ] `systems` has one entry per configured role read, `tracker` and
      `test_manager`, each with `server` equal to the server `vogon.yaml`
      names for that role.
- [ ] `issues` holds every issue whose summary starts with a record id or a
      test node id, found with the role's search tool, and every issue a
      record's `tracked_as` names for that role, read by key.
- [ ] Each issue has `key`, `summary`, the full `description` as stored, and
      `status`. A test issue has `links`: the requirement issues it is linked
      to.
- [ ] `transitions` lists every status change from the issue's history,
      oldest first, each with `to`, `by` as the email the system reports for
      the person who made it, and `at`.
- [ ] A transition carries `description` when the description has changed
      since that transition: the description as it stood at that time, read
      from the history. It is absent when the description is unchanged since.
- [ ] A test issue has `executions`: every result imported against it, with
      `build`, `at` and `outcome`.
- [ ] A key a `tracked_as` names that the system does not return goes under
      `missing`, with `reason` such as `deleted` or `not found`.
- [ ] Values are copied as the system returns them. Nothing is inferred,
      filled in or reformatted, except timestamps into ISO 8601.

## Planning

- [ ] `vogon push --plan` is run after the read, and its output is the plan.
      An error it reports is shown to the person and is not worked around.
- [ ] The person is shown every line it printed, and nothing is written
      until the person confirms. `no changes` means nothing is written.
- [ ] A record or test reported as requiring re-approval is shown to the
      person with the role that approves it again.

## Applying

- [ ] The writes applied are exactly the `writes` in `.vogon/push_plan.json`,
      each once, in the file's order. No write is added, dropped or changed.
- [ ] Each write goes to the server in its `server` field:
  - [ ] `create`: an issue with the `summary` and `description` as given;
        for a test issue, then a link to each key in `links`;
  - [ ] `update`: each field in `fields` set to its `to` value;
  - [ ] `link`: the test issue `key` linked to the requirement issue `to`;
  - [ ] `import`: the result `outcome` against the test issue `key`, with
        the build `build`;
  - [ ] `track`: no call; it goes into the keys file below.
- [ ] Nothing else is written to the tracker or the test manager at this step.
- [ ] When a write fails, the remaining writes are not applied. The keys
      created so far are recorded as below, the issues are read again, and
      the plan is made again.

## Recording the keys

- [ ] The keys the system created, and the plan's `track` entries, are saved
      to `.vogon/push_created.json` as a list of
      `{"id": ..., "role": ..., "key": ...}`, the `id` and `role` taken from
      the write that created the key.
- [ ] `vogon push --record .vogon/push_created.json` writes them into the
      records' `tracked_as`. The records are never edited by hand for this.
- [ ] The issues are read again into `.vogon/tracker.json`, and
      `vogon push --plan` then prints `no changes`.
- [ ] `vogon check` reports no error, and the `tracked_as` changes are
      committed with a message naming the record ids.

## After the step

- [ ] At step 5 and step 10 the person is told which role approves the new
      issues, from `approvals.requirements` or `approvals.test_cases` in
      `vogon.yaml`, and in which system. `SKILL.md` states what VOGON does
      not do about that approval.
- [ ] At step 15 no coverage report or traceability matrix is produced. The
      test manager produces them from the links and results (`REQ-TRC-7`),
      and step 16 files them following `references/evidence.md`.
