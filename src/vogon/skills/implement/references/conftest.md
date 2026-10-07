# Test markers in the host project

The changes below copy the marker ids into the JUnit XML properties. Make each
change the host project lacks; skip one whose lines are present.

## conftest.py

In `conftest.py` in the directory that holds the pytest configuration, or at
the repository root where there is none, add exactly these lines:

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

## Marker registration

If the pytest configuration (`pyproject.toml`, `pytest.ini`, `setup.cfg` or
`tox.ini`) requires registered markers (`--strict-markers` or `--strict` in
`addopts`, or `strict_markers` or `strict` set true) or turns warnings into
errors (`error` in `filterwarnings`, or `-W error` in `addopts`), add to its
`markers` list `req: requirement ids the test verifies` and
`procedure: test procedure ids the test follows`.
