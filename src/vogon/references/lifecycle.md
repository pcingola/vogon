# Requirement lifecycle

## Requirement approver

The requirement approver is the role named in the "Approval" section of
`vogon/project/requirements.md`. When that section names no role, the
requirement approver is the Product Owner, `product_owner` in `vogon.yaml`.

## Approval

- The tracker holds approvals when `vogon.yaml` names a tracker and
  `vogon/project/tracking.md` states an approval transition for the
  requirement item type. In every other case, `vogon approve` records
  approvals in the state file.
- Where no tracker holds approvals, a requirement is approved when its
  `REQ-*.json` on the default branch has an `approved` entry after its latest
  `changed` entry.
- Where a tracker holds approvals, the tracker item is the only record of
  approval. No skill writes an `approved` entry, and no skill copies an
  approval or tracker text into the repository.
  - The tracker item is the one whose key is in the `issue` field of a
    `drafted` or `changed` entry.
  - The requirement is approved when both hold: the item reached the approved
    state through the transition `tracking.md` names, and that transition is
    dated after the latest `changed` entry.
- Where a tracker holds approvals and the requirement text in the item
  differs from `REQ-*.md`, report the difference. The developer resolves it
  as a change to the requirement.

## Needs approval again

A requirement needs approval again when a `changed` entry follows its latest
approval. Its approval is then stale.

## Implemented

A requirement is implemented when an `implemented` entry links a merged pull
request or a commit on the default branch, and the entry is dated on or after
the latest `changed` entry. Without a `changed` entry, the `implemented`
entry is compared with the `drafted` entry.

## In progress

A requirement is in progress when either of these holds:

- an open pull request names the requirement id in its title, its description
  or one of its commits;
- a pushed branch that is not merged holds a `planned` entry for it.

## Missing approval

A skill that works on a requirement that is not approved, or whose approval is
stale, does the work. It reports the missing approval in the session and in
its pull request description, naming the requirement approver and the system
where the approval is given.

## Change to an approved requirement

A skill changes an approved requirement only with the agreement of the
developer running it. An instruction from the developer to withdraw or
supersede the requirement is that agreement. The skill appends a `changed`
entry to `REQ-*.json` in the same pull request as the change to `REQ-*.md`,
and lists the requirement as needing approval again in the pull request
description. The skill also does each step `vogon/project/requirements.md`
"Change to an approved requirement" lists.

## Withdrawal and supersession

The developer withdraws or supersedes a requirement with `vogon:requirements`.
`records.md` states the status values.

- Withdrawal: the reason comes from the developer's instruction or a held
  source.
- Supersession: draft the replacing requirement with a new id from
  `vogon id`. Set the old requirement to `status: {superseded_by: <new id>}`
  in the same pull request.
- A withdrawn or superseded requirement needs approval again only when a
  `changed` entry follows its latest approval. `vogon:approve` skips every
  other withdrawn or superseded requirement.
- Where the requirement has a tracker item, the skill updates the item as for
  any change and performs no transition. It reports the item key, so that a
  person moves the item to the state the tracker uses for a withdrawn
  requirement.
- The skill reports every test marker, test procedure `verifies` list, plan
  and `depends_on` that names the old id, and changes none of them.

## State file

Append each entry to a `REQ-*.json` once and never edit it.

A state file is `{"id": "<requirement id>", "steps": [<entry>, ...]}`.
Every entry has `step` and `date`, `yyyy-mm-dd`, taken from
`date '+%Y-%m-%d'` unless the entry states otherwise. `pr` is a pull request
number, `commit` a commit hash, and a person is `Name <email>`.

```json
{"step": "drafted", "date": "<yyyy-mm-dd>", "pr": <number>, "issue": "<tracker key>"}
{"step": "changed", "date": "<yyyy-mm-dd>", "pr": <number>, "issue": "<tracker key>"}
{"step": "approved", "date": "<yyyy-mm-dd>", "by": "<Name> <email>", "via": "vogon approve"}
{"step": "planned", "date": "<yyyy-mm-dd>", "commit": "<plan commit>", "plan": "vogon/plans/plan_<slug>.md", "approved_by": "<Name> <email>"}
{"step": "test_procedures_written", "date": "<yyyy-mm-dd>", "pr": <number>}
{"step": "implemented", "date": "<yyyy-mm-dd>", "pr": <number>, "commit": "<last code commit>"}
{"step": "released", "date": "<yyyy-mm-dd>", "commit": "<release commit>", "release": "<release>", "pr": <number>}
```

- `changed`: written for every change to `REQ-*.md` after its `drafted`
  entry, by the skill that makes the change, whether or not the requirement
  was approved. A withdrawal and a supersession are changes and have no step
  of their own. `pr` is the pull request that changes `REQ-*.md`.
- `approved`: written by `vogon approve`, only where no tracker holds
  approvals.
- `planned`: written by `vogon:implement` when the plan is committed before
  code is written. `commit` is the commit that holds the plan. `approved_by`
  is present only when a developer approved the plan: the approving
  developer's identity from `git config user.name` and `git config user.email`
  in their session. A plan committed again after a
  change gets a new entry.
