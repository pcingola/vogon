# FAKE-REQ — Changes that need no requirement

Some changes implement no requirement: typo fixes, refactoring, formatting,
dependency updates, build and CI fixes. Such a change names `FAKE-REQ` in a
commit message or in the pull request description, followed by a sentence
saying what the change does. `vogon change` accepts a change that names
`FAKE-REQ` in place of a record id.

A change that adds or changes behaviour does not use `FAKE-REQ`. It names the
requirement it implements, and if there is none, the requirement is written
first.

Example: "FAKE-REQ — fix a typo in the installation guide."
