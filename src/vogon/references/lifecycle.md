# Requirement lifecycle

## Requirement approver

The requirement approver is the role named in the "Approval" section of
`vogon/project/requirements.md`. When that section names no role, the
requirement approver is the Product Owner, `product_owner` in `vogon.yaml`.

## Approval

- When `vogon.yaml` names a tracker, read `vogon/project/tracking.md`. If it
  states an approval transition for the requirement item type, the tracker
  holds approvals. Otherwise `vogon approve` records approvals in the state
  file.
- Where no tracker holds approvals, a requirement is approved when its
  `REQ-*.json` on the default branch has an `approved` entry after its latest
  `changed` entry. Report an `approved` entry that is on an open pull request
  branch and not on the default branch.
- Where a tracker holds approvals, the tracker item is the only record of
  approval. No skill writes an `approved` entry, and no skill copies an
  approval or tracker text into the repository.
  - The tracker item is the one whose key is in the `issue` field of a
    `drafted` or `changed` entry. Read it through the tracker.
  - The requirement is approved when both hold: the item reached the approved
    state through the transition `tracking.md` names, and that transition is
    dated after the latest `changed` entry.
  - A requirement with no entry with an `issue` field has not been sent to
    the tracker and is not approved.
- Where a tracker holds approvals and the requirement text in the item
  differs from `REQ-*.md`, report the difference. The developer resolves it
  as a change to the requirement.

## Needs approval again

A requirement needs approval again when a `changed` entry follows its latest
approval. Its approval is then stale.

## Implemented

A requirement is implemented when an `implemented` entry links a merged pull
request or a commit on the default branch, and the entry is dated on or after
the latest `changed` entry. A requirement with no `changed` entry uses its
`drafted` entry.

- An `implemented` entry whose pull request is not merged, or whose commit is
  not on the default branch, does not count. Report it.
- An `implemented` entry dated before the latest `changed` entry means the
  change is not implemented. Report it.

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
supersede the requirement is that agreement. The skill:

1. changes `REQ-*.md`;
2. appends a `changed` entry to `REQ-*.json` in the same pull request;
3. lists the requirement as needing approval again in the pull request
   description;
4. tells the requirement approver.

`vogon/project/requirements.md` "Change to an approved requirement" lists the
further steps the validation plan requires for the change.

## Withdrawal and supersession

The developer withdraws or supersedes a requirement with `vogon:requirements`.
`records.md` states the status values.

- Withdrawal: set `status: withdrawn` and state the reason in the body. The
  reason comes from the developer's
  instruction or a held source.
- Supersession: draft the replacing requirement with a new id from
  `vogon id`. Set the old requirement to `status: {superseded_by: <new id>}`
  in the same pull request.
- Both are changes to `REQ-*.md` and get a `changed` entry. A missing
  approval of the change is reported as for any change.
- A withdrawn or superseded requirement waits for approval only when its
  latest approval is followed by a `changed` entry. `vogon:approve` selects
  no other withdrawn or superseded requirement.
- Where the requirement has a tracker item, the skill updates the item as for
  any change and performs no transition. It reports the item key, so that a
  person moves the item to the state the tracker uses for a withdrawn
  requirement.
- The skill reports every test marker, test procedure `verifies` list, plan
  and `depends_on` that names the old id, and changes none of them.

## State file

Append each entry to a `REQ-*.json` once and never edit it. When the entry
records a pull request, open the pull request first. Then append the entry
with its `pr` number, commit the file and push it to the same branch.

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

- `issue`, on `drafted` or `changed`: the key of the tracker item the skill
  created in the same run. When a requirement's tracker item is first created
  during a change, `issue` goes on that `changed` entry.
- `drafted`: written by `vogon:requirements` for each new requirement. `pr`
  is the pull request that adds it.
- `changed`: written for every change to `REQ-*.md` after its `drafted`
  entry, by the skill that makes the change, whether or not the requirement
  was approved. A withdrawal and a supersession are changes and have no step
  of their own. `pr` is the pull request that changes `REQ-*.md`.
- `approved`: written by `vogon approve`, only where no tracker holds
  approvals. It names no pull request or commit. `by` is the git identity
  `vogon approve` reads, `date` the day it runs, and `via` is
  `vogon approve`.
- `planned`: written by `vogon:implement` when the plan is committed before
  code is written. It names no pull request. `commit` is the commit that holds
  the plan. `approved_by` is present only when a developer approved the plan:
  the approving developer's identity from `git config user.name` and
  `git config user.email` in their session. A plan committed again after a
  change gets a new entry.
- `test_procedures_written`: written by `vogon:tests`. `pr` is the pull
  request the skill opens.
- `implemented`: written by `vogon:implement` after it opens the pull
  request. `commit` is the last code commit.
- `released`: written by `vogon:release`. `release` is the release name, and
  `pr` the release pull request.
