---
name: requirements
description: Drafts requirements, domain facts, constraints and decisions from meetings, mail, chat, documents and code, withdraws and supersedes requirements, and opens the pull request. TRIGGER when: user says draft requirements, requirements from a meeting, mail, chat, document or code, "withdraw REQ-", "supersede REQ-".
---

# vogon:requirements

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   `requirements.md`, and `tracking.md` where `vogon.yaml` names a tracker.
2. For each meeting, mail thread or chat channel, a sub-agent downloads it to
   `vogon/tmp/` and writes its summary in `vogon/sources/` (`sources.md`).
   No record is drafted from a summary, and it is not committed, until its
   review passes.
3. For each attached, shared or named file, a sub-agent files the original
   and its markdown copy (`sources.md`).
4. A sub-agent drafts the records in the format of `records.md` and the
   requirement form of `requirements.md`. It applies each withdrawal and
   supersession the developer instructed (`lifecycle.md` "Withdrawal and
   supersession"). The review applies `records.md` and
   `${CLAUDE_PLUGIN_ROOT}/skills/requirements/references/requirement-checklist.md`.
5. For each requirement whose only source is code, ask the developer to
   confirm that the behaviour is intended.
6. Run `vogon id --check` and renumber each id it reports. Open the pull
   request.
7. Where a tracker is configured, create or update the tracker item of each
   new or changed requirement with the item type, fields and links
   `tracking.md` names.
8. Append a `drafted` entry for each new requirement and a `changed` entry
   for each changed one (`lifecycle.md` "State file"). Commit and push.
9. Tell the requirement approver (`lifecycle.md` "Requirement approver") which
   requirements wait for approval and where.
