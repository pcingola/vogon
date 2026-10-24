# Requirement checklist

The default checklist for each drafted requirement.

Each requirement:

- [ ] costs less than the failure it prevents. The requirement is a finding
      when:
      - the work it requires runs far more often than the event it guards
        against occurs;
      - a cheaper form meets the same need (checking once at setup, on change
        or on failure);
      - it adds steps, confirmations or files to a person's work that no
        source asks for;
- [ ] contradicts no other requirement, constraint or decision, including
      those in open pull requests, unless it names the decision it reverses;
- [ ] has `gxp_impact` and `risk` values that do not follow from how hard the
      requirement is to build or test.
