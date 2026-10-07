# Test procedure checklist

The default checklist for a test procedure.

Apply each item to the procedure against its requirement. Report each failed
item as a finding with its evidence: the step number, and the sentence of the
requirement or its source the finding rests on.

1. Every acceptance criterion of the requirement is covered by at least one
   step. Name each criterion no step covers.
2. Each step has one action and one expected result. A step with two actions,
   or with no expected result, is a finding.
3. Each expected value comes from the requirement or its sources. A value
   that appears in neither, or that is taken from the code, a test or a run of
   the code, is a finding. Quote the value and say where it appears.
4. A tester can carry out each step in the formal test environment that
   `tests.md` names, from the procedure alone: every input, precondition and
   location the step needs is stated, and nothing in it depends on the
   developer's machine or on knowledge not written in the procedure.
