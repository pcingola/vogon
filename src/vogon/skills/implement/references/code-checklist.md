# Code checklist

The default checklist for the code and documentation of one part of a plan.

The evaluator reads the requirements the part covers, the plan entry for the
part, the code the part changed, and the documentation it changed or should
have changed. Each item the part fails is a finding, with the file and line.

- [ ] The code does what each requirement of the part states, for every
      acceptance criterion the plan entry assigns to the part.
- [ ] The code does nothing the requirements and the plan entry do not ask
      for.
- [ ] Structured data uses defined data structures and classes, such as
      dataclasses or typed models, and not dictionaries passed between
      functions.
- [ ] Regulated data keeps its integrity: no data is lost or overwritten
      without a trace, timestamps are in one time zone, and every change to
      regulated data is attributable to a user.
- [ ] No secret, credential or personal data is in the code or the test data.
- [ ] The documentation describes the code as it is after the change. A
      document, docstring or comment that describes removed or changed
      behaviour is a finding.
