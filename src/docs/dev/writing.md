# Writing standard

One standard for everything: this documentation, the records in `vogon/`, the
text VOGON writes into a tracker, and the drafting instructions VOGON ships
to a host project. A record written to this standard and a page of this
documentation read the same way, because the reader is the same person.

The satirical voice in the brand guide applies to the marketing page and to
nothing else. Not the README, not script output, not any record, not any tracker
field, and not any document VOGON generates.

## The reader

An engineer who knows software and does not know your domain, and does not
know compliance. They are competent and short of time. They are reading to
find out what to build, or to check that what was built matches what was
asked.

That reader sets every rule below. A document they cannot act on has failed,
however complete it is.

## Rules

Plain declarative sentences. Precise terms. The shortest wording that is still
exact.

Define or link every domain term at first use. A record may not use a term it
has neither explained in a clause nor linked to the record that explains it.
This applies to compliance vocabulary as much as to the application domain.

State the fact and let the reader judge its weight. No "critically",
"importantly", "notably", "it is worth noting", "the key insight", "here is
the thing".

No metaphors for importance. Nothing is load-bearing, a linchpin, a gate, a
forcing function or a north star.

No marketing or management vocabulary, and no coined labels. If a label stands
in for a plain description, write the plain description.

Do not build to a conclusion. State it first and support it after. A reader
who stops at the first sentence should have the answer.

No clickbait. A heading names its section; it does not tease it or summarise a
verdict.

No filler. Delete any sentence that would not change the reader's
understanding if it were removed.

Every sentence means one thing on the first reading. If the reader has to work
out what was meant, the sentence is wrong however elegant it is.

No three-item lists built for rhythm, no "not X, but Y", no em-dash aside used
only for emphasis, no rhetorical question answered by the next sentence, no
closing line that restates the opening.

Do not count things that can change. Not "seven skills", not "the four
checks", not "twelve requirements", and not "all 35 tests pass". Name them, or
refer to the set without sizing it. A count is correct on the day it is
written and wrong afterwards, and nothing in review catches it. A set fixed by
definition, such as the four kinds of record, may be counted because adding to
it is a change to the definition. This applies to what VOGON generates as much
as to what is written here: a generated document names the requirements it
covers, it does not say how many there are.

Do not carry vocabulary across from a document you just read. A record drafted
from a slide deck is written in this standard, not in the deck's words.

## What a document does not contain

A document states what is settled. It has no section of open questions, open
issues, TODOs, TBDs or next steps. An unresolved question is raised with a
person and answered; it is not filed.

An absent field is absent. Never `N/A`, never "none considered", never an empty
list. A record with no example has no example block, and that hole is the
signal that it has not been thought through.

## Length

If a record's description runs past a short paragraph it is probably two
records. Split it rather than lengthening it. Length is the usual symptom of a
requirement that has not been decomposed.

A record is finished when the reader above could implement it without asking a
question. Not when it is comprehensive. Those are different, and the second
produces documents nobody reads.

## What a tool can check

Most of this is a judgement a person makes in review. A checker enforces the
part that is mechanical, and claims nothing about the rest. `vogon check`
applies the checks below to every record (`REQ-REC-8`).

Passing the checks does not mean the prose is good. Failing one means it is
not.

### Banned words and phrases

A word or phrase from this list is reported wherever it appears in a record's
title or body. The match ignores case and is on whole words, and text inside
a code span or a code block is not matched, so a record can quote a term in
backticks.

| Rule | Words and phrases |
| --- | --- |
| No emphasis in place of a fact | critically, crucially, importantly, notably, worth noting, it should be noted, needless to say, the key insight, here is the thing |
| No metaphors for importance | load-bearing, linchpin, gate, gatekeeper, forcing function, north star, cornerstone, silver bullet, game-changer |
| No marketing or management vocabulary | leverage, seamless, seamlessly, synergy, best-in-class, world-class, cutting-edge, state-of-the-art, next-generation, holistic, empower, unlock, streamline, value proposition, paradigm shift, move the needle, deep dive, low-hanging fruit, wedge, land-and-expand |

The list is extended in a reviewed change to this page and to the checker
together.

### Other checks

- A placeholder where a field should be absent. A frontmatter value of `N/A`,
  `n/a`, `NA`, `TBD`, `TODO`, `none considered`, `-`, `null`, an empty string
  or an empty list is reported. So is `none`, except in `gxp_risk`, where it
  is one of the allowed values.
- A heading phrased as a question: a heading or a bold block label ending in
  `?`.
- A section heading or bold block label naming open questions, open issues,
  TODO, TBD or next steps.
- A cardinal number, in digits or in words, standing before a plural noun
  that names something the repository holds: skills, commands, requirements,
  records, tests, checks, modules. The example block is exempt, because it
  describes an illustrative situation rather than the repository.
- A body longer than the limit for its record type. The limits are in
  [Records](records.md#length-limits).

The satirical voice is checked separately: no fixed string from the brand
guide may appear in a record, a tracker field, script output, or any file
VOGON writes under `vogon/` (`REQ-GEN-5`). The checker holds its own copy of
those strings, because the brand guide is not part of the plugin.
