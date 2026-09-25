# From meetings to requirements

A developer asks the agent to create requirements from last week's meetings on
barcode printing.

1. The agent gets every meeting from last week that has a transcript and
   decides which ones concern the project and the topic from three things:
   the meeting title, the participants, and a summary of the transcript.
   The project's configuration file lists the project's people and their
   roles, so the agent matches the participants against it: a meeting
   attended by the project's Product Owner and developers is likely to be
   about the project, and one with none of them is likely not.
2. For each relevant meeting it downloads the transcript to a temporary
   directory outside the repository, writes a summary, checks the summary
   against the transcript, and deletes the transcript. A transcript can
   hold personal remarks, names and discussion unrelated to the project, so
   it is never committed and does not outlive its summary.
3. It saves each summary in the repository as a source, with the meeting
   date, the participants as the meeting lists them, and the meeting's
   identifier in the meeting system.
   From here on the summary is the only input, so any developer on any
   machine can continue the work.
4. It reads the summaries and sorts what was said: things the system must
   do (requirements), things that are true of the domain (facts), limits
   imposed from outside (constraints), choices the team made (decisions),
   and questions nobody answered. It drafts a record for each, citing the
   summary, and a requirement gets acceptance criteria.
5. It checks the drafts against the summaries (below), then runs the checks
   of [Checking the new requirements](new_requirements.md). Nothing is committed or sent anywhere until both are done.

Checks on the choice of meetings:

- A meeting left out is about another project or topic, and its title,
  participants or summary show it. A meeting whose title looks unrelated
  but whose participants and summary are the project's is kept.

Checks on each summary, made before its transcript is deleted:

- The summary says only what the transcript says.
- It keeps everything the records will be drafted from: every requirement,
  fact, constraint, decision and unanswered question the meeting stated,
  with the values given and who stated it, named as the transcript names
  them. Where the configuration file lists that person, their project role
  is added.
- A statement that was proposed and then rejected or changed later in the
  meeting is kept as it ended, not as it was first said.
- It holds nothing personal and nothing unrelated to the project: no
  personal remarks, no health or HR matters, no opinions about people.

Checks on the drafted records, against the summaries:

- Each record says what its passage in the summary says, no more. Where the
  passage is vague, the record is not made precise by guessing; the gap
  becomes a question.
- A statement changed in a later meeting is recorded as it stands in the
  latest summary.
- A statement made in two meetings is one record citing both summaries.
- A "must" is a requirement when the configuration file lists the person
  who stated it in a role that decides it, such as the Product Owner.
  Otherwise, including when the speaker is not in the configuration file,
  it is recorded as a proposal for the Product Owner. An idea floated in
  discussion is not a requirement.
- Each statement is classified correctly: a requirement can be failed by a
  test, a fact is true whether or not the system is built, a constraint is
  imposed from outside, a decision is a choice among options.
- Every value in an acceptance criterion comes from the summary. A value
  the meeting did not give becomes a question, not a guess.

The requirements are proposals until the Product Owner accepts them in the
tracker.
