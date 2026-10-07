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
- [ ] has `gxp_impact` and `risk` values that follow from their reasons.
