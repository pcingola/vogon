"""pytest plugin that records the outcome of every test carrying a `req` marker.

`vogon trace` loads it with `-p vogon_pytest` and puts this directory on
`PYTHONPATH`. The directory holds this file and nothing else, so no other
module of the scripts can shadow a module of the host project's tests. It runs
inside the host project's Python environment, so it imports only the standard
library; pytest calls its hooks.

It registers the `req` marker, so a run through `vogon trace` also works in a
project whose pytest configuration does not declare it.

The results file is written at the end of the session to the path in the
environment variable `VOGON_RESULTS`, or to `.vogon/results.json` under the
pytest root directory when that variable is unset. It is JSON:

    {
      "format": 1,
      "build": "<full commit hash>" | null,
      "tests": [
        {
          "nodeid": "tests/test_x.py::test_y[1]",
          "requirements": ["REQ-TRC-1", "REQ-TRC-6"],
          "outcome": "passed"
        }
      ]
    }

`build` is the value of the environment variable `VOGON_BUILD`, or null when
it is unset or empty. `vogon trace` sets it to `git rev-parse HEAD` only when
the working tree has no uncommitted change, and sets it back to null if the
commit or a tracked file changed during the run (REQ-TRC-6). Results whose
`build` is null are never imported.

`tests` holds one entry per test item that carries at least one `req` marker,
from the function, its class or the module, in the order the tests ran.
`requirements` is the ids the markers name, each once: the module's first,
then the class's, then the function's.
`outcome` is one of:

- `passed`, `failed`, `skipped`
- `error`: setup or teardown failed
- `xfailed`: marked `xfail` and failed; `xpassed`: marked `xfail` and passed
"""

from __future__ import annotations

import json
import os
from pathlib import Path

FORMAT = 1
MARKER = "req"
RESULTS_ENV = "VOGON_RESULTS"
BUILD_ENV = "VOGON_BUILD"
DEFAULT_RESULTS = Path(".vogon") / "results.json"
MARKER_LINE = "req(*ids): the requirement ids the test verifies"


class Recorder:
    def __init__(self, path: Path, build: str | None) -> None:
        self.path = path
        self.build = build
        self.requirements: dict[str, list[str]] = {}
        self.outcomes: dict[str, str] = {}

    def pytest_collection_modifyitems(self, items) -> None:
        for item in items:
            ids: list[str] = []
            # iter_markers yields the function's markers first; reversed, the module's come first.
            for mark in reversed(list(item.iter_markers(name=MARKER))):
                for arg in mark.args:
                    if str(arg) not in ids:
                        ids.append(str(arg))
            if ids:
                self.requirements[item.nodeid] = ids

    def pytest_runtest_logreport(self, report) -> None:
        if report.nodeid not in self.requirements:
            return
        xfail = hasattr(report, "wasxfail")
        current = self.outcomes.get(report.nodeid)
        if report.when == "setup":
            if report.failed:
                self.outcomes[report.nodeid] = "error"
            elif report.skipped:
                self.outcomes[report.nodeid] = "xfailed" if xfail else "skipped"
        elif report.when == "call":
            if report.passed:
                self.outcomes[report.nodeid] = "xpassed" if xfail else "passed"
            elif report.skipped:
                self.outcomes[report.nodeid] = "xfailed" if xfail else "skipped"
            else:
                self.outcomes[report.nodeid] = "failed"
        elif report.when == "teardown" and report.failed and current in (None, "passed", "xpassed"):
            self.outcomes[report.nodeid] = "error"

    def pytest_sessionfinish(self, session) -> None:
        tests = [{"nodeid": nodeid, "requirements": self.requirements[nodeid], "outcome": outcome}
                 for nodeid, outcome in self.outcomes.items()]
        document = {"format": FORMAT, "build": self.build, "tests": tests}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", MARKER_LINE)
    target = os.environ.get(RESULTS_ENV)
    path = Path(target) if target else Path(config.rootpath) / DEFAULT_RESULTS
    build = os.environ.get(BUILD_ENV) or None
    config.pluginmanager.register(Recorder(path, build), "vogon-recorder")
