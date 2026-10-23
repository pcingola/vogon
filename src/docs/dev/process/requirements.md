# Requirements from sources

Steps 2 to 4 of the [steps](index.md). A developer runs `vogon:requirements`
and names the sources: meetings, mail threads and chat channels by id, title or
date range; documents; files attached or shared; code with its history, pull
requests and issues. The steps are in
`src/vogon/skills/requirements/SKILL.md`.

The skill files a checked summary of each meeting, thread or channel and the
original and markdown copy of each document in `vogon/sources/`
([Sources](../sources.md)). Downloads stay in `vogon/tmp/` and are deleted
before the commit. It drafts the records from the checked summaries and
documents ([Records](../records.md)) and checks them in
[the loop](../architecture.md#the-loop).

A change to an approved requirement is proposed to the developer running the
skill, and the record is changed only with their agreement. Findings that need
a choice, questions no source answers, and requirements whose only source is
code also go to that developer before the pull request is opened.

The pull request lists the requirements drafted and changed, and those that
need approval again. Where a tracker is configured, the skill creates or
updates a tracker item per new or changed requirement. Each new requirement gets a `drafted`
entry and each changed approved requirement a `changed` entry in its
`REQ-*.json`. The skill tells the Product Owner what waits for approval
([Approving requirements](approval.md)).
