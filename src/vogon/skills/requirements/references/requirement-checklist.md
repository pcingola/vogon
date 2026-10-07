# Requirement checklist

The default checklist the requirement evaluator of `vogon:requirements` applies
to each drafted requirement.

Each requirement:

- [ ] makes sense in practice. The evaluator states, from the sources, the
      records and what is known of the systems involved: the situation the
      requirement responds to and how often it occurs; how often the work the
      requirement asks for runs and what each run costs; and what goes wrong, for whom, if
      the requirement is not met. It is a finding when the work runs far more
      often than the situation occurs, when meeting the requirement costs
      more than the failure it prevents, when a cheaper form meets the same
      need (checking once at setup, on change or on failure), or when it adds
      steps, confirmations or files to a person's work that nobody would miss;
- [ ] contradicts no other requirement, constraint or decision, including
      those in open pull requests;
- [ ] does not contradict the project's design as its decision records state
      it, or names the decision it reverses;
- [ ] is not a duplicate and is not already covered by another requirement;
- [ ] can be tested, and every expected value comes from the source;
- [ ] states one thing, with one reading;
- [ ] says only what its cited source passage says: a requirement the cited
      passage does not support is a finding;
- [ ] has `gxp_impact` and `risk` values that follow from their reasons.
      `gxp_impact` names what a failure would damage: patient safety, product
      quality, or data integrity (data that loses an ALCOA+ property:
      attributable, legible, contemporaneous, original, accurate, complete,
      consistent, enduring, available), or none. Neither value follows from
      how hard the requirement is to build or test.

Across the drafted records, a statement in a source that states a
requirement, constraint, fact or decision and that no record carries, and
that no existing record already covers, is a finding against the set.
