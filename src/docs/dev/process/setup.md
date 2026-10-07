# Setting up a project

A developer installs VOGON into the project's repository and asks the agent to
set it up. This is step 1 of the [steps](steps.md), done once per project and
again when a system or a role holder changes.

1. The agent finds, among the MCP servers connected to Claude Code, the server
   for each system role: meeting system, repository host, tracker, test
   manager, document system. With one candidate it uses it. With several, the developer
   chooses, because only the developer knows which one company policy
   requires.
2. For the tracker and the test manager, it reads the workflow through the
   chosen server and proposes as approved the states whose names say approval
   or signature, and reports a transition into an approved state that does
   not make the approver re-enter their credentials, because such a
   transition is not an electronic signature.
3. It asks the developer for the people holding each role, as emails, the
   developers included.
4. It shows everything it filled in as one list. The developer confirms or
   corrects it in one answer.
5. It writes `vogon.yaml` at the root of the repository and commits it.
6. It drafts the validation plan into `vogon/documents/validation_plan.md`:
   the system and its GAMP category, the roles and their holders, the systems
   used, the documents each release produces, how risk sets the testing, and
   what must hold for release. A second agent checks it. The plan goes to the
   System Owner and the Quality Manager for approval: by pull request review
   in the prototype, in the document system in a deployment. No result counts
   as evidence before the plan is approved (`DEC-027`).

```yaml
systems:
  meeting_system: {server: acme-meetings}
  repository_host: {server: github}
  tracker: {server: github, approved_states: [Approved]}
roles:
  developer: [dev@example.com, dev2@example.com]
  product_owner: [po@example.com]
  test_lead: [testlead@example.com]
  system_owner: [owner@example.com]
  quality_manager: [qm@example.com]
```

The roles are the ones the [steps](steps.md) use. Where a company's procedure
gives an approval to another role from [Vocabulary](../vocabulary.md#who-signs-what),
such as requirements approved by the Business Process Owner, the role holding
that approval is listed under the name the procedure uses, in place of the
default.

A system role is reached only through the server named for it. A role absent
from `systems` is not used, and the steps that need it report that they were
skipped.

Checks on the configuration:

- Every role that gives an approval in the [steps](steps.md) has at least one
  holder.
- No person holds both the Quality Manager role and the developer or Test
  Lead role.
- Each configured server provides the operations the skills need from its
  role: reading and creating issues, reading transitions, registering tests,
  importing results, filing documents.

Later, every skill that reads an approval reports one given by someone who
does not hold the role, or by an author of what was approved (`CON-002`).
