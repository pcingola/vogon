# Compliance documents

1. For the release, the agent drafts the documents the validation package
   needs: the risk assessment, the test specification, the design
   specification and the test report. Each is drawn from the requirements,
   the tests, and the results of the build being released, and cites them.
2. A second agent checks each draft. Findings go back until none remain.
3. The agent imports the test results of the released build into the test manager,
   files the documents in the document system, and tells each approver what
   is waiting for them.
4. The Test Lead approves the test specification, and the System Owner and
   the Quality Manager sign the package, in the document system.
5. The agent checks what was filed against what was built, and reports any
   difference.

Checks on every document:

- Every statement follows from a requirement, a test, a result or the code,
  and cites it.
- It describes the build being released, and every result in it comes from
  that build.
- It agrees with the other documents: the same requirements, the same risk
  levels, the same build.
- It claims no approval or signature.

Checks on each document:

- Risk assessment: every requirement in the release has a risk level with
  its reasoning, the level agrees with the requirement, and a higher risk
  has more thorough testing.
- Test specification: every test in the release is described with what it
  checks, its inputs and its expected values, and they match the test code.
- Design specification: it describes the code as built, and where the code
  differs from a plan, it follows the code.
- Test report: every test's outcome for the release build is given; every
  failed or skipped test is named with how it was handled.

Checks after filing:

- The filed copies are identical to what was drafted and exported.
- Nothing approved has changed since its approval: no requirement, test or
  document was edited after it was signed.
- Every approval came from a person holding the role, who is not an author
  of what they approved, and came before what it governs was used.
