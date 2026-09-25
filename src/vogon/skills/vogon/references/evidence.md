# Evidence (step 16)

Moving the test manager's traceability report and results for the released
build into the document system, unchanged, and checking the filed copies with
`vogon evidence` (`REQ-TRK-10`). Each item below is a rule the filing meets or
fails.

## The build

- [ ] The build is the one the person names as released. It is not chosen
      by Claude Code.
- [ ] It is written as the test manager records it, normally the full commit
      hash `vogon trace` recorded, and is the `<build>` in every path and
      command below.
- [ ] The test issues hold results imported for that build at step 15, as
      read into `.vogon/tracker.json`. Without them the step stops and the
      person is told.

## Exporting

- [ ] The traceability report and the results for the build are exported
      from the server `vogon.yaml` names for `test_manager`, with the tools
      mapped to `export_traceability_report` and `export_results` in
      `.vogon/servers.json`.
- [ ] Each export is saved under `.vogon/evidence/<build>/export/` as the
      bytes the server returned, with no conversion, reformatting or edit.
- [ ] Each file name contains the build, so the filed copy names it too.
- [ ] Nothing under `.vogon/evidence/<build>/export/` comes from another
      build. A directory left from an earlier attempt for the same build is
      emptied before the export.
- [ ] Before filing, each exported file names the build in its file name or
      its content. A file that does not is not filed, and the person is told.
- [ ] VOGON produces neither report. A missing or wrong export is reported
      to the person, not replaced with a report VOGON wrote (`REQ-TRC-7`).

## Filing

- [ ] Each exported file is filed through the server `vogon.yaml` names for
      `document_system`, with the tool mapped to `upload_document`, under the
      same file name, with the same bytes.
- [ ] Only the files in `.vogon/evidence/<build>/export/` are filed. No file
      of another build is filed at this step.
- [ ] With no `test_manager` or no `document_system` configured, the step is
      not done and the person is told which role is not configured.

## Reading back and checking

- [ ] Each filed document is read back with the tool mapped to
      `download_document` and saved under `.vogon/evidence/<build>/filed/`
      with the same relative path as its export, as the bytes returned.
- [ ] `vogon evidence <build>` is run and reports no error.
- [ ] An error is shown to the person verbatim, with the filed document it
      names. The filed document is not changed, replaced or removed by Claude
      Code; the person decides what is done with it.

## After the step

- [ ] The person is told that the package is ready for sign-off at step 17,
      by the roles `approvals.release` in `vogon.yaml` names, in the document
      system.
