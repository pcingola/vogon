"""One module per `vogon` subcommand.

Each module defines:

    NAME: str                                   the subcommand name
    HELP: str                                   one line for `vogon --help`
    add_arguments(parser) -> None               the subcommand's own arguments
    run(args, config) -> Iterable[Finding]      does the work; may print its own output

`cli.py` lists the modules in `COMMANDS`, one line each, and prints the
findings `run` returns. The exit status is non-zero only when a finding is a
failure (REQ-CLI-1).
"""
