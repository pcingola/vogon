# Writing standard (every step that writes prose)

Applies to records, plans, documents, summaries, test names and docstrings,
commit messages, pull request descriptions and every tracker field. Each item
below is a rule the text meets or fails. `vogon check` enforces the
mechanical part on records; the rest is checked by reading.

## The reader

An engineer who knows software, does not know the application domain or
compliance, and is short of time. The text is finished when that reader can
act on it without asking a question, not when it is comprehensive.

## Sentences

- [ ] Plain declarative sentences and precise terms, in the shortest wording
      that is still exact.
- [ ] Each sentence means one thing on the first reading.
- [ ] The conclusion comes first and the support after it.
- [ ] Every domain and compliance term is linked at first use to the record
      or document that explains it, or explained in a clause taken from an
      input file. A term no input explains is not given a definition.

## Support

- [ ] Every statement about the system, the domain or a regulation follows
      from an input file given to the step: a record, a held document, the
      plan, a test, a result, or the code where the step names it as input.
      That holds for definitions, reasons and consequences as well.
- [ ] A statement no input supports is not written. A cited passage says what
      the text says it does.
- [ ] No sentence that could be deleted without changing what the reader
      understands.
- [ ] The weight of a fact is left to the reader. No word or phrase from the
      list below.
- [ ] No three-item list built for rhythm, no "not X, but Y", no dash aside
      used only for emphasis, no rhetorical question answered by the next
      sentence, no closing line that restates the opening.
- [ ] No coined label standing in for a plain description.
- [ ] Vocabulary is not carried over from the source just read. A record
      drafted from a deck is written in this standard, not in the deck's words.
- [ ] No joke, pun, or product voice. The text reads as a technical record.
- [ ] A role is named, never the person holding it.

## Banned words and phrases

Matched ignoring case, on whole words, outside code spans and code blocks.

- Emphasis in place of a fact: critically, crucially, importantly, notably,
  worth noting, it should be noted, needless to say, the key insight, here is
  the thing.
- Metaphors for importance: load-bearing, linchpin, gate, gatekeeper, forcing
  function, north star, cornerstone, silver bullet, game-changer.
- Marketing or management vocabulary: leverage, seamless, seamlessly,
  synergy, best-in-class, world-class, cutting-edge, state-of-the-art,
  next-generation, holistic, empower, unlock, streamline, value proposition,
  paradigm shift, move the needle, deep dive, low-hanging fruit, wedge,
  land-and-expand.

## Structure

- [ ] A heading names its section. It does not tease it, summarise a verdict,
      or end in `?`. Neither does a bold block label.
- [ ] No section or label for open questions, open issues, TODO, TBD or next
      steps. An unresolved question is asked of the person, not written down.
- [ ] An absent field is absent: no `N/A`, `n/a`, `NA`, `TBD`, `TODO`,
      `none considered`, `-`, `null`, empty string or empty list. `none` only
      as a `gxp_risk` value.

## Counts

- [ ] No count of something that can change: no number, in digits or words,
      before skills, commands, requirements, records, tests, checks or
      modules. Name them, or refer to the set without sizing it. A generated
      document names the requirements it covers and does not count them.
- [ ] An example block may count, because it describes an illustration.
- [ ] A set fixed by definition, such as the four kinds of record, may be
      counted.

## Length

- [ ] A record description longer than a short paragraph is split into two
      records.
- [ ] A record body is within its word limit: requirement 300, fact 200,
      constraint 200, decision 600.
