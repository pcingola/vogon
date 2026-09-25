"""`vogon check`: run every check that needs no external system.

A check is a function `check(config) -> Iterable[Finding]`, listed in CHECKS.
"""

from __future__ import annotations

from typing import Callable, Iterable

import config as config_module
import writing
from checks import markers, records, sources
from checks import snapshots
from config import Config
from findings import Finding

NAME = "check"
HELP = "Check the configuration, records and test markers."


def configuration(config: Config) -> Iterable[Finding]:
    """What reading `vogon.yaml` reported."""
    return config.findings


CHECKS: list[Callable[[Config], Iterable[Finding]]] = [
    configuration,
    config_module.check,
    writing.check,
    *records.CHECKS,
    *sources.CHECKS,
    *markers.CHECKS,
    *snapshots.CHECKS,
]


def add_arguments(parser) -> None:
    pass


def run(args, config: Config) -> list[Finding]:
    findings: list[Finding] = []
    for check in CHECKS:
        findings.extend(check(config))
    return findings
