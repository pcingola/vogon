# Requirement ids in tests, commits and code

- Each test names the requirements it verifies in
  `@pytest.mark.req("<id>", ...)`, and only those.
- Where test procedures exist, each test also names the procedures it follows
  in `@pytest.mark.procedure("<id>", ...)`.
- A marker that names a withdrawn or superseded requirement is a finding.
- Each commit message names the requirements the commit implements.
  Implementation code names no requirement id.

## Changes in the host project

The changes below copy the marker ids into the JUnit XML properties.
`vogon:init` makes each change the host project lacks and skips one whose
lines are present. Every other skill that writes or reads markers reports
each missing change and tells the developer to run `vogon:init`.

### conftest.py

Add exactly these lines to `conftest.py` in the directory of the pytest
configuration file, or at the repository root when there is none:

```python
def pytest_collection_modifyitems(items):
    for item in items:
        for name in ("req", "procedure"):
            for marker in item.iter_markers(name):
                for value in marker.args:
                    item.user_properties.append((name, value))
```

If that `conftest.py` already defines `pytest_collection_modifyitems`, do not
define it twice: add the `for item in items:` loop at the end of the existing
function, and add `items` to its parameters if it lacks it.

### Marker registration

The pytest configuration is `pyproject.toml`, `pytest.ini`, `setup.cfg` or
`tox.ini`. Add to its `markers` list `req: requirement ids the test verifies`
and `procedure: test procedure ids the test follows` when any of these holds:

- `addopts` contains `--strict-markers`, `--strict` or `-W error`;
- `strict_markers` or `strict` is set true;
- `filterwarnings` contains `error`.
