# Code checklist

The default checklist for the code and documentation of one part of a plan.

The evaluator reads the requirements the part covers, the plan entry for the
part, the code the part changed, and the documentation it changed or should
have changed. Each item the part fails is a finding, with the file and line.

- [ ] The code does what each requirement of the part states, for every
      acceptance criterion the plan entry assigns to the part.
- [ ] The code does nothing the requirements and the plan entry do not ask
      for.
- [ ] The code is well written: clear names, one responsibility per function
      and class, no duplicated logic, errors handled where they occur.
- [ ] The code is not overengineered: no abstraction, option, layer or
      extension point that no requirement uses.
- [ ] Structured data uses defined data structures and classes, such as
      dataclasses or typed models, and not dictionaries passed between
      functions.
- [ ] The code follows the language's other best practices and the host
      project's existing conventions, such as its use of type hints,
      formatting, imports, error types and module layout.
- [ ] Requirement ids do not appear in implementation code.
- [ ] The documentation describes the code as it is after the change. A
      document, docstring or comment that describes removed or changed
      behaviour is a finding.
