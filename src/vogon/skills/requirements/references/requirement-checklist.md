# Requirement checklist

The default checklist the requirement evaluator of `vogon:requirements` applies
to each drafted requirement.

Each requirement:

- [ ] costs less than the failure it prevents. The evaluator states, from the
      sources, the records and what is known of the systems involved: the
      situation the requirement responds to and how often it occurs; how often
      the work the requirement asks for runs and what each run costs; and what
      goes wrong, for whom, if the requirement is not met. It is a finding
      when:
      - the work runs far more often than the situation occurs;
      - a cheaper form meets the same need (checking once at setup, on change
        or on failure);
      - it adds steps, confirmations or files to a person's work that no
        source asks for;
- [ ] contradicts no other requirement, constraint or decision, including
      those in open pull requests, unless it names the decision it reverses;
- [ ] is not a duplicate and is not already covered by another requirement;
- [ ] can be tested;
- [ ] states one thing, with one reading;
- [ ] has `gxp_impact` and `risk` values that follow from their reasons.
      `gxp_impact` names what a failure would damage, from the values in
      `records.md`. Data integrity is damaged when data loses an ALCOA+
      property: attributable, legible, contemporaneous, original, accurate,
      complete, consistent, enduring, available. Neither value follows from
      how hard the requirement is to build or test.

A requirement, constraint, fact or decision stated in a source that no
drafted or existing record covers is a finding against the set of drafted
records.
