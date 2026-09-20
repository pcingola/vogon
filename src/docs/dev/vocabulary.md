# Vocabulary

What the words mean. How to write a record is in [Records](records.md).

This file exists because projects call four different kinds of statement
"requirements" and keep them in one list under one numbering scheme. Rows
stating what the system must do sit next to rows stating how a third-party
platform behaves, next to a decision not to build something. Most of those rows
cannot be tested, and a module file reads as a transcript.

## The two projects

VOGON is one codebase installed into another, and both keep records in `gxp/`
in the same format, so the two are named apart.

**VOGON project** — this repository. VOGON's own code, documentation and
records.

**Host project** — a project VOGON is installed into, holding that project's
own code, tests and records. **User project** means the same thing; host
project is the term used in the documentation.

A statement about `gxp/` applies to both unless it names one.

## The four kinds of record

Everything written down that the system will be built from is one of four
things. Each has its own id namespace and its own file.

**Requirement** — something the system must do. Written as a MUST statement
saying what has to be true rather than how to achieve it, and phrased so that a
test could fail it. Ids are `REQ-<MODULE>-<NUMBER>`.

**Domain fact** — something true whether or not this project exists. "An Xray
test issue is linked to the requirement issue it verifies" is a fact; nobody on
the project chose it and no test of ours can fail it. Prefix `FACT-`.

**Constraint** — a limit imposed from outside that design cannot trade away: a
regulation, a company procedure, or a platform behaviour. "Approval cannot be
performed by a machine account" is a constraint. Prefix `CON-`.

**Decision** — a choice made among options, recorded with what the options cost
and what the choice commits us to. Choosing *not* to build something is a
decision. Prefix `DEC-`.

A fifth thing, the **elicitation record**, is the meeting summary or source
document a record came from. It is evidence, cited by records, and never a
record itself.

## Verbs

[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) as clarified by
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174): only the uppercase form is
binding, so an ordinary "must" or "should" in prose carries no weight.

| Word | Means |
| --- | --- |
| **MUST**, **MUST NOT** | A requirement. Binding. The only form a requirement record is written in |
| **SHOULD**, **SHOULD NOT** | A recommendation. Not binding, and not a requirement |
| **MAY** | Permission |
| *(no modal verb)* | A statement of fact, about the world or about something outside our control |

"Results imported into Xray sometimes arrive without a build identifier" has no
modal verb, so it is a domain fact. "VOGON MUST reject a result import with no
build identifier" is the requirement beside it.

"shall" is not used here. ISO/IEC/IEEE 29148 uses it, and the ISO drafting
rules it follows forbid "must" as an alternative, but those rules govern how ISO
standards are written. No regulation in this field, and no part of GAMP 5, EU
Annex 11 or 21 CFR Part 11, says which modal verb a requirement uses; they
require that it be unambiguous, testable, uniquely identified and traceable. A
formal User Requirements Specification in "shall" is generated from these
records, and the substitution is mechanical.

## Compliance terms

| Term | What it is |
| --- | --- |
| **GxP** | The umbrella label for regulations covering work a regulator relies on |
| **ICH** | The body that writes the guidelines the FDA, EMA and others adopt |
| **ISPE** | A pharmaceutical engineering industry association |
| **GAMP 5** | ISPE's guide to validating a computerised system so an inspector accepts it. Second Edition, 2022. A guide, not a law |
| **GAMP category 5** | Custom-written software, the category with the most scrutiny |
| **21 CFR Part 11** | The US regulation on electronic records and electronic signatures |
| **EU Annex 11** | The European counterpart to Part 11 |
| **ALCOA+** | A checklist of properties regulated data must have: attributable, legible, contemporaneous, original, accurate, plus complete, consistent, enduring, available |
| **Validation** | Producing evidence that you specified what the system should do, built to that, and verified it |
| **CSV / CSA** | The two names for validating software in this industry; CSA is the FDA's more recent risk-based framing |
| **URS** | User Requirements Specification: the controlled document holding approved requirements |
| **RTM** | Requirements Traceability Matrix: requirement to design to test to result, for every requirement |
| **Xray** | A Jira plugin that records test runs and produces requirement coverage and traceability reports |

## Who signs what

A validated system's documents are signed by roles named in the validation
plan; a separate approval matrix says which person holds each role.

| Role | What this person normally does | Formal role in validation |
| --- | --- | --- |
| **System Owner** | One named person on the IT side. Answers for the software for as long as it runs: available, supported, secure, and changed only through change control | Signs the technical documents and chairs the change control board. Cannot be empty at release |
| **Business Process Owner** | One named person from the business side who knows how the work is actually done and answers for that process | Approves the requirements and decides the finished system is fit to use. Cannot be empty at release |
| **IT Quality Manager** | One named person outside the build team. Checks that the validation process was followed: documents exist, were approved before use, and agree with each other | Signs the validation plan and the summary report. Must be independent of the people building the system |
| **Business Quality Manager** | One named person outside the build team, on the business side. Checks that the process the system supports still complies | Signs alongside the IT Quality Manager, under the same independence rule |
| **Change control board** | A standing group that meets after release. For each proposed change it decides whether the change is allowed and what has to be re-tested before it ships | The mechanism by which a validated system is allowed to change. Required once the system is live |
| **Validation lead** | One named person who writes the validation plan and the summary report and assembles the evidence into a package someone can audit | Author, not approver |
| **Subject Matter Expert** | Anyone who knows the domain or the technology well enough to write or review a document. Not an appointment | Writes and reviews documents. Never approves them, because an approver may not be the author |
| **Product Owner** | One named person who owns the backlog and decides what gets built next | None. Signs nothing in the validation package |

These are not rubber stamps and they are not headcount. A signature names who
is answerable if the thing turns out to be wrong, which is why the approver of
a document may not be its author. One person can hold several roles, subject to
two rules: Quality is independent of the people building the system, and nobody
approves their own work.

An electronic signature is not a typed name or a pasted image. The signer
re-enters their own credentials, and what is stored against that version of
that record is their printed name, the date and time, and what the signature
means — authored, reviewed or approved. It cannot be moved onto a later edit.

## Where these terms come from

- **ISO/IEC/IEEE 29148:2018**, the requirements engineering standard:
  requirement attributes (identifier, statement, rationale, source,
  verification method, status), the characteristics a well-formed requirement
  has, and `constraint` as a defined term. Its "shall" convention is [not
  followed here](#verbs).
- **RFC 2119 and RFC 8174** — MUST, SHOULD and MAY, and the rule that only the
  uppercase forms are binding.
- **ISPE GAMP 5, Second Edition (2022)** — user requirement, the requirements
  traceability matrix, and per-requirement risk classification.
- **The architecture decision record** is a convention from a 2011 post by
  Michael Nygard, not a standard.
- **One file per record, named by id, grouped by id prefix** follows Doorstop,
  the closest existing tool for keeping requirements in git.
- **`domain fact`** is local to this project. The nearest standard equivalents
  are 29148's *assumptions and dependencies* and the business-analysis term
  *domain knowledge*, and neither names what these files hold.
