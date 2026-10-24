# Vocabulary

Projects often keep four kinds of statement in one requirements list under one
numbering. Most of those rows cannot be tested. VOGON keeps them as four kinds
of record.

## The two projects

VOGON is one codebase installed into another, so the two are named apart.

**VOGON project**: this repository. VOGON's own code and documentation, and
its constraints and decisions in `vogon/`.

**Host project**: a project VOGON is installed into, holding that project's
own code, tests and records. **User project** means the same thing; host
project is the term used in the documentation.

## The four kinds of record

Everything written down that the system will be built from is one of four
kinds of record. Each has its own id namespace and its own file
([Records](records.md)). Test procedures are records too, with the id prefix
`TP`, but they describe how a requirement is verified and are defined under
Tests below.

**Requirement**: something the system must do. Written as a MUST statement
saying what has to be true and not how, so that a test could fail it. Ids are
`REQ-<MODULE>-<NUMBER>`, or `REQ-<NUMBER>` in a project without modules.

**Domain fact**: something true whether or not this project exists. "A test
item in the test manager is linked to the tracker item of the requirement it
verifies" is a fact; nobody on the project chose it and no project test can
fail it. Prefix `FACT-`.

**Constraint**: a limit imposed from outside that design cannot trade away: a
regulation, a company procedure, or a platform behaviour. "Approval cannot be
performed by a machine account" is a constraint. Prefix `CON-`.

**Decision**: a choice made among options, recorded with what the options cost
and what the choice commits the project to. Choosing *not* to build something is
a decision. Prefix `DEC-`.

The reviewed summary or held document a record came from is a source
([Sources](sources.md)). Records cite it; it is never a record itself.

## Verbs

[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) as clarified by
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174): only the uppercase form is
binding, so an ordinary "must" or "should" in prose carries no weight.

| Word | Means |
| --- | --- |
| **MUST**, **MUST NOT** | A requirement. Binding. The only form a requirement record is written in |
| **SHOULD**, **MAY** | Not used in a record. A statement in this form is not a requirement |
| *(no modal verb)* | A statement of fact, about the world or about something outside the project's control |

"Results imported into the test manager sometimes arrive without a build
identifier" has no modal verb, so it is a domain fact. "VOGON MUST reject a
result import with no build identifier" is the requirement beside it.

VOGON writes MUST, not "shall". ISO/IEC/IEEE 29148 uses "shall"; GAMP 5, EU
Annex 11 and 21 CFR Part 11 prescribe no modal verb, only that a requirement be
unambiguous, testable, uniquely identified and traceable.

## Systems

| Term | What it is |
| --- | --- |
| **Tracker** | The issue tracker holding work items such as requirements, with their priority and assignee. Where the project approves in the tracker, it also holds the approvals. VOGON 0.1 is tested with Jira |
| **Test manager** | The system holding test cases, test runs and results, which produces the coverage and traceability reports. VOGON 0.1 is tested with Xray. A project may have none |
| **Repository host** | The service holding the git repository and reviewing changes before they merge. VOGON 0.1 is tested with GitHub |
| **Document system** | The controlled document management system where the validation package is filed and signed |

## Tests

| Term | What it is |
| --- | --- |
| **Acceptance criteria** | The part of a requirement that states what must be tested. Approved with the requirement |
| **Test** | A pytest function. Its `req` marker names the requirements it verifies. A test with a `req` marker is the test case for those requirements |
| **Test procedure** | A document, not code: numbered steps in prose, each with its expected result, with an id and linked to its requirement. Projects call it a test script, test protocol or manual test case; VOGON says test procedure, because "script" reads as code. Written and approved as `tests.md` states |

## Who signs what

A validated system's documents are signed by roles named in the validation
plan, as the project process files state them. The requirement approver is
defined in `src/vogon/references/lifecycle.md` "Requirement approver".
`vogon.yaml` lists the people who hold each role, so records and generated
documents name the role and never the person. The roles below are common ones;
a project uses the roles its plan names.

| Role | What this person normally does | Formal role in validation |
| --- | --- | --- |
| **Product Owner** | One named person who owns the backlog and decides what gets built next | Approves the requirements where `requirements.md` names this role or no role, with `vogon:approve` or in the tracker. `vogon.yaml` lists the holders under `product_owner` |
| **Test Lead** | One of the engineers, named to review the test procedures | Approves the test procedures and test documents the validation plan assigns to this role, as `tests.md` and `documents.md` state |

## Where these terms come from

- **ISO/IEC/IEEE 29148:2018**, the requirements engineering standard:
  requirement attributes (identifier, statement, rationale, source,
  verification method, status), the characteristics a well-formed requirement
  has, and `constraint` as a defined term. Its "shall" convention is [not
  followed here](#verbs).
- **RFC 2119 and RFC 8174**: MUST, SHOULD and MAY, and the rule that only the
  uppercase forms are binding.
- **ISPE GAMP 5, Second Edition (2022)**: user requirement, the requirements
  traceability matrix, and per-requirement risk classification.
- **The architecture decision record** is a convention from a 2011 post by
  Michael Nygard, not a standard.
- **One file per record, named by id, grouped by id prefix** follows Doorstop,
  the closest existing tool for keeping requirements in git.
- **`domain fact`** is local to this project. The nearest standard equivalents
  are 29148's *assumptions and dependencies* and the business-analysis term
  *domain knowledge*, and neither names what these files hold.
