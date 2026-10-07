# Requirements from sources

Steps 2 to 5 of the [steps](index.md). A developer runs `vogon:requirements`
and names the sources, for example last week's meetings on barcode printing,
a mail thread and a specification.

## Sources

The skill reads any source the session's MCP connectors reach:

- meetings, mail threads and chat channels, named by id, title or date range;
- documents, by path or by their location in the document system;
- files attached to a mail, posted in a chat or shared in a meeting;
- code, with its documentation, git history, pull requests and issues.

## Step 2: file the sources

Transcripts, mail and chat hold personal data, and some countries restrict
keeping meeting transcripts. Each is downloaded to `vogon/tmp/`, which is
gitignored, and never committed. One writing sub-agent per meeting, thread or
channel writes a summary, and an evaluator checks it against the download:
every statement is supported, and nothing that bears on requirements is left
out. The checked summary is filed in `vogon/sources/` with the source's id in
its system, its date and its participants. The download is then deleted.

An attached or shared file, and a document the developer names, is a document
and is kept. It is filed in `vogon/sources/` as the original with a markdown
copy beside it. One sub-agent reads the copy and writes an extract: each
statement that bears on requirements, with its location, such as the page or
slide. An evaluator checks the extract against the file. A long file is read
only in that sub-agent's context.

[Sources](../sources.md) gives the file names and frontmatter.

## Step 3: draft the records

A writing sub-agent drafts the records from the checked summaries, the checked
extracts and the code. It classifies each statement as a requirement, domain
fact, constraint or decision ([Records](../records.md)), cites the summaries
and markdown copies it rests on, and writes each requirement with its
acceptance criteria and its four risk fields. Each record takes its id from
`vogon id`. A source that changes an existing record changes it in place.

## Step 4: check the records

Two evaluators check the drafts. One applies the requirement checklist
([Architecture](../architecture.md#loops)) against the drafts, the existing
records, the records in open pull requests and the cited sources. The other
reports every requirement whose only source is the code, because code shows
current behaviour, defects included.

The loop fixes what it can. A finding that needs a choice, a question no
source answers, and a requirement drawn from code alone go to the developer
running the skill, before anything is committed. A finding on a requirement
the Product Owner already approved goes to the Product Owner, as a change that
needs approval again.

## Step 5: send the requirements for approval

The skill commits the summaries, the filed documents and the records on a
working branch and opens a pull request. Its description lists the
requirements drafted and changed, each changed requirement that needs approval
again, and the loops run with their rounds and open findings. Where a tracker
is configured, the skill creates one tracker item per new requirement, as
`tracking.md` states, and updates the items of changed requirements. It writes
each requirement's `REQ-*.json` with a `drafted` entry.

The skill reports the sources it used and those it left out, and tells the
Product Owner which requirements wait for approval and where
([Approving requirements](approval.md)).
