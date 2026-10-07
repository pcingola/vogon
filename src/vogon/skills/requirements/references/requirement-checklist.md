# Requirement checklist

The default checklist the requirement evaluator of `vogon:requirements` applies
to each drafted requirement.

Each requirement:

- [ ] makes sense in practice: it solves a real problem, and its cost fits how
      often the situation occurs;
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
