# Pytest - Notes

## 1. Installation and configuration

| Task | Command |
|---|---|
| Installation | `pip install pytest` |
| Version | `pytest --version` |
| Virtual environment | `python -m venv venv` |
| Activation (Linux/Mac) | `source venv/bin/activate` |
| Activation (Windows) | `venv\Scripts\activate` |
| Save dependencies | `pip freeze > requirements.txt` |
| Install from file | `pip install -r requirements.txt` |

Plugins: `pytest-mock`, `pytest-cov`, `pytest-xdist`, `pytest-html`.

**pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

---

## 2. Test structure and naming

| Element | Convention |
|---|---|
| File | `test_*.py` or `*_test.py` |
| Function | `test_*` |
| Class | `Test*` (no `__init__`) |
| Method in a class | `test_*` |

```python
def dodaj(a, b):
    return a + b

def test_dodaj():
    assert dodaj(2, 3) == 5
```

- A test is a regular function, with no `return`, using `assert`.
- Names are case-sensitive (`Test_dodaj` will not be discovered).

---

## 3. Running tests

| Command | Action |
|---|---|
| `pytest` | all tests |
| `pytest -v` | verbose (test names) |
| `pytest -q` | quiet/short |
| `pytest file.py` | a single file |
| `pytest file.py::test_function` | a single function |
| `pytest tests/` | a folder |
| `pytest -x` | stop after the first failure |
| `pytest -s` | show `print()` output |
| `pytest --tb=short / long / no` | traceback verbosity |

---

## 4. Assert

```python
def test_lista():
    assert [1, 2, 3] == [1, 2, 3]

def test_z_komunikatem():
    x = 5
    assert x > 10, f"x should be > 10, but is {x}"
```

| Check | Syntax |
|---|---|
| equality | `assert a == b` |
| element in a collection | `assert x in lista` |
| element missing | `assert x not in lista` |
| float numbers | `assert 0.1 + 0.2 == pytest.approx(0.3)` |

- pytest automatically shows the values on both sides of the comparison (assertion introspection).

---

## 5. Testing exceptions — `pytest.raises`

```python
import pytest

def test_dzielenie_przez_zero():
    with pytest.raises(ZeroDivisionError):
        10 / 0

def test_komunikat():
    with pytest.raises(ValueError, match="negative"):
        waliduj_wiek(-5)

def test_exc_info():
    with pytest.raises(ValueError) as exc_info:
        waliduj_wiek(-5)
    assert "negative" in str(exc_info.value)
```

| Element | Meaning |
|---|---|
| `match="..."` | checks the message (regex) |
| `exc_info.value` | the exception object |
| `exc_info.type` | the exception class |
| no exception raised | `Failed: DID NOT RAISE` |

---

## 6. Fixtures

```python
import pytest

@pytest.fixture
def dane():
    return [1, 2, 3]

def test_suma(dane):
    assert sum(dane) == 6
```

**Teardown via `yield`:**

```python
@pytest.fixture
def polaczenie():
    print("opening")
    yield "connection"
    print("closing")
```

| Rule | Description |
|---|---|
| Usage | fixture name as a test argument |
| `return` | returns data |
| `yield` | code after `yield` = teardown |
| Fixture using a fixture | one fixture can take another as an argument |
| Exception in a fixture | test status: `ERROR` |

### Scope and autouse

| scope | Runs |
|---|---|
| `function` (default) | for every test |
| `class` | once per class |
| `module` | once per file |
| `session` | once for the whole run |

```python
@pytest.fixture(scope="module")
def baza():
    yield "database"

@pytest.fixture(autouse=True)
def log_startu():
    print("--- test starting ---")
```

- `autouse=True` — runs automatically, without being passed as an argument.
- Broad scope + mutated data = tests affecting one another.

---

## 7. conftest.py

- Fixtures from `conftest.py` are available throughout the folder and its subfolders — no import needed.
- You can have multiple `conftest.py` files; the one closer to the test overrides the more general one (same fixture name).

```
tests/
  conftest.py          # general fixtures
  api/
    conftest.py        # fixtures for API tests
    test_users.py
```

| Command | Action |
|---|---|
| `pytest --fixtures` | list available fixtures |

---

## 8. Parametrize

```python
@pytest.mark.parametrize("a, b, oczekiwany", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_dodawanie(a, b, oczekiwany):
    assert a + b == oczekiwany
```

| Feature | Description |
|---|---|
| two `parametrize` on one test | Cartesian product of combinations (3×2 = 6 tests) |
| `ids=[...]` | custom case names in the report |
| `parametrize` + `pytest.raises` | multiple invalid inputs, same exception |

**Parametrizing a fixture:**

```python
@pytest.fixture(params=[1, 2, 3])
def liczba(request):
    return request.param
```

---

## 9. Markers

| Marker | Action | Report status |
|---|---|---|
| `@pytest.mark.skip(reason="...")` | always skipped | SKIPPED |
| `@pytest.mark.skipif(condition, reason="...")` | skipped conditionally | SKIPPED |
| `@pytest.mark.xfail(reason="...")` | expected failure | XFAIL / XPASS |
| `@pytest.mark.xfail(strict=True)` | unexpected success = error | FAILED |
| `@pytest.mark.name` | custom marker | — |

```python
import sys

@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10+")
def test_nowa_skladnia():
    ...

@pytest.mark.smoke
def test_logowanie():
    ...
```

**Registering custom markers** (without this: an `unknown marker` warning):

```ini
[pytest]
markers =
    smoke: fast basic tests
    slow: long-running tests
```

Run with: `pytest -m smoke`

---

## 10. setup / teardown (classic style)

| Method | When |
|---|---|
| `setup_function` / `teardown_function` | before/after every test function |
| `setup_method` / `teardown_method` | before/after every method in a class |
| `setup_class` / `teardown_class` | once per class |
| `setup_module` / `teardown_module` | once per file |

```python
class TestKonto:
    def setup_method(self):
        self.saldo = 100

    def teardown_method(self):
        self.saldo = 0

    def test_wplata(self):
        self.saldo += 50
        assert self.saldo == 150
```

Order for a class with two tests:
`setup_class` → `setup_method` → test 1 → `teardown_method` → `setup_method` → test 2 → `teardown_method` → `teardown_class`

**Fixtures instead of setup/teardown:** parametrization, different scopes, explicit dependencies.

---

## 11. Mocking

| Tool | Use case |
|---|---|
| `monkeypatch` (built-in) | replacing attributes, functions, environment variables; automatic rollback |
| `unittest.mock.patch` / `MagicMock` | replacing objects + checking calls |
| `pytest-mock` (`mocker`) | convenient interface to `unittest.mock` |

**monkeypatch:**

```python
def test_status(monkeypatch):
    class FakeResp:
        def json(self):
            return {"status": "ok"}

    monkeypatch.setattr("requests.get", lambda url: FakeResp())
    assert pobierz_status() == "ok"

def test_env(monkeypatch):
    monkeypatch.setenv("TRYB", "test")
```

**unittest.mock:**

```python
from unittest.mock import patch

@patch("requests.get")
def test_z_mockiem(mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}
    assert pobierz_status() == "ok"
    mock_get.assert_called_once()
```

| Method / attribute | Checks |
|---|---|
| `assert_called_once()` | called exactly once |
| `assert_called_with(...)` | last call with given arguments |
| `call_count` | number of calls |

---

## 12. Reporting results

| Option | Action |
|---|---|
| `--junitxml=report.xml` | JUnit XML report (for CI) |
| `--html=report.html --self-contained-html` | HTML report (`pip install pytest-html`) |
| `--durations=N` | N slowest tests |
| `-s` | show `print()` output |
| `-v` / `-q` | more / fewer details |

---

## 13. Filtering tests

| Command | Action |
|---|---|
| `pytest -k "expression"` | tests by name (`and`, `or`, `not`) |
| `pytest -m name` | tests with a marker |
| `pytest -m "a or b"` | tests with either marker |
| `pytest file.py::Class::test_method` | a specific test (node id) |
| `pytest --collect-only` | list tests without running them |
| `pytest --lf` | only the last failed tests |
| `pytest --ff` | failed tests first, then the rest |

Example: `pytest -k "login and not admin"`

---

## 14. Project organization and configuration

**pyproject.toml:**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
markers = [
    "smoke: fast basic tests",
    "slow: long-running tests",
]
```

| Option | Meaning |
|---|---|
| `testpaths` | where to look for tests |
| `addopts` | options added to every run |
| `markers` | marker registration (`pytest --markers` shows the list) |

- When `pytest.ini` exists, it takes precedence over `pyproject.toml`.

```
project/
  src/
  tests/
    conftest.py
    unit/
      test_kalkulator.py
    api/
      conftest.py
      test_users_api.py
  pyproject.toml
```

---

## 15. pytest + requests

| `Response` element | Content |
|---|---|
| `.status_code` | HTTP status code |
| `.json()` | body as a dict/list |
| `.text` | body as text |
| `.headers` | headers |

```python
import requests

def test_get_status_ok():
    odp = requests.get("https://jsonplaceholder.typicode.com/posts/1")
    assert odp.status_code == 200

def test_get_zawartosc():
    dane = requests.get("https://jsonplaceholder.typicode.com/posts/1").json()
    assert dane["id"] == 1
    assert "title" in dane
```

| HTTP method | Example | Typical status |
|---|---|---|
| GET | `requests.get(url)` | 200 |
| POST | `requests.post(url, json={...})` | 201 |
| PUT / PATCH | `requests.put(url, json={...})` | 200 |
| DELETE | `requests.delete(url)` | 200 / 204 |
| nonexistent resource | — | 404 |

---

## 16. API testing — techniques

```python
BASE_URL = "https://jsonplaceholder.typicode.com"

@pytest.mark.parametrize("post_id, status", [(1, 200), (999999, 404)])
def test_pobranie_posta(post_id, status):
    assert requests.get(f"{BASE_URL}/posts/{post_id}").status_code == status

def test_typy_pol():
    dane = requests.get(f"{BASE_URL}/posts/1").json()
    assert isinstance(dane["id"], int)
    assert isinstance(dane["title"], str)

def test_timeout():
    with pytest.raises(requests.exceptions.Timeout):
        requests.get(f"{BASE_URL}/posts/1", timeout=0.001)
```

| Technique | Use case |
|---|---|
| `parametrize` | multiple endpoints / cases |
| `isinstance` | validating JSON field types |
| `timeout=` | protection against a hanging test |
| fixture with `BASE_URL` | a single place for the base address |

---

## 17. Sessions, authentication, and test data

**Session with a token:**

```python
@pytest.fixture(scope="session")
def sesja_api():
    s = requests.Session()
    s.headers.update({"Authorization": "Bearer FAKE_TOKEN"})
    yield s
    s.close()

def test_z_sesja(sesja_api):
    assert sesja_api.get(f"{BASE_URL}/posts/1").status_code == 200
```

- `requests.Session()` keeps headers and cookies between requests.
- `scope="session"` — login/token is prepared once for the whole run.

**Test data from JSON:**

```python
import json

with open("dane_testowe.json", encoding="utf-8") as f:
    PRZYPADKI = json.load(f)

@pytest.mark.parametrize("przypadek", PRZYPADKI)
def test_uzytkownicy(przypadek):
    assert "email" in przypadek
```

---

## 18. pytest + GitHub Actions

File: `.github/workflows/tests.yml`

```yaml
name: Pytest tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest -v --junitxml=report.xml
      - uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: report.xml
```

| Element | Meaning |
|---|---|
| `on:` | triggers (push, pull_request) |
| `actions/checkout` | checks out the code |
| `actions/setup-python` | selects the Python version |
| `run:` | a shell command |
| `upload-artifact` | saves the report as an artifact |

Run only smoke tests on a PR: `pytest -m smoke`
