# Pytest - notatki

## 1. Instalacja i konfiguracja

| Zadanie | Komenda |
|---|---|
| Instalacja | `pip install pytest` |
| Wersja | `pytest --version` |
| Wirtualne środowisko | `python -m venv venv` |
| Aktywacja (Linux/Mac) | `source venv/bin/activate` |
| Aktywacja (Windows) | `venv\Scripts\activate` |
| Zapis zależności | `pip freeze > requirements.txt` |
| Instalacja z pliku | `pip install -r requirements.txt` |

Plugins: `pytest-mock`, `pytest-cov`, `pytest-xdist`, `pytest-html`.

**pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

---

## 2. Struktura i nazewnictwo testów

| Element | Konwencja |
|---|---|
| Plik | `test_*.py` lub `*_test.py` |
| Funkcja | `test_*` |
| Klasa | `Test*` (bez `__init__`) |
| Metoda w klasie | `test_*` |

```python
def dodaj(a, b):
    return a + b

def test_dodaj():
    assert dodaj(2, 3) == 5
```

- Test = zwykła funkcja, bez `return`, z `assert`.
- Nazwy są wrażliwe na wielkość liter (`Test_dodaj` nie zostanie znaleziony).

---

## 3. Uruchamianie testów

| Komenda | Działanie |
|---|---|
| `pytest` | wszystkie testy |
| `pytest -v` | szczegółowo (nazwy testów) |
| `pytest -q` | krótko |
| `pytest plik.py` | jeden plik |
| `pytest plik.py::test_funkcja` | jedna funkcja |
| `pytest tests/` | folder |
| `pytest -x` | stop po pierwszym błędzie |
| `pytest -s` | pokazuje `print()` |
| `pytest --tb=short / long / no` | szczegółowość tracebacku |

---

## 4. Assert

```python
def test_lista():
    assert [1, 2, 3] == [1, 2, 3]

def test_z_komunikatem():
    x = 5
    assert x > 10, f"x powinno być > 10, a jest {x}"
```

| Sprawdzenie | Zapis |
|---|---|
| równość | `assert a == b` |
| element w kolekcji | `assert x in lista` |
| brak elementu | `assert x not in lista` |
| liczby float | `assert 0.1 + 0.2 == pytest.approx(0.3)` |

- pytest sam pokazuje wartości po obu stronach porównania (assertion introspection).

---

## 5. Testowanie wyjątków — `pytest.raises`

```python
import pytest

def test_dzielenie_przez_zero():
    with pytest.raises(ZeroDivisionError):
        10 / 0

def test_komunikat():
    with pytest.raises(ValueError, match="ujemny"):
        waliduj_wiek(-5)

def test_exc_info():
    with pytest.raises(ValueError) as exc_info:
        waliduj_wiek(-5)
    assert "ujemny" in str(exc_info.value)
```

| Element | Znaczenie |
|---|---|
| `match="..."` | sprawdza komunikat (regex) |
| `exc_info.value` | obiekt wyjątku |
| `exc_info.type` | klasa wyjątku |
| brak wyjątku | `Failed: DID NOT RAISE` |

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

**Teardown przez `yield`:**

```python
@pytest.fixture
def polaczenie():
    print("otwieram")
    yield "polaczenie"
    print("zamykam")
```

| Zasada | Opis |
|---|---|
| Użycie | nazwa fixture jako argument testu |
| `return` | zwraca dane |
| `yield` | kod po `yield` = teardown |
| Fixture w fixture | jedna fixture może przyjmować inną jako argument |
| Wyjątek w fixture | status testu: `ERROR` |

### Scope i autouse

| scope | Uruchomienie |
|---|---|
| `function` (domyślny) | dla każdego testu |
| `class` | raz na klasę |
| `module` | raz na plik |
| `session` | raz na cały przebieg |

```python
@pytest.fixture(scope="module")
def baza():
    yield "baza"

@pytest.fixture(autouse=True)
def log_startu():
    print("--- start testu ---")
```

- `autouse=True` — uruchamia się automatycznie, bez podawania jako argument.
- Szeroki scope + modyfikowane dane = testy wpływają na siebie.

---

## 7. conftest.py

- Fixtures z `conftest.py` są dostępne w całym folderze i podfolderach — bez importu.
- Można mieć wiele `conftest.py`; bliższy testowi nadpisuje ogólniejszy (ta sama nazwa fixture).

```
tests/
  conftest.py          # fixtures ogólne
  api/
    conftest.py        # fixtures dla testów API
    test_users.py
```

| Komenda | Działanie |
|---|---|
| `pytest --fixtures` | lista dostępnych fixtures |

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

| Funkcja | Opis |
|---|---|
| dwa `parametrize` na jednym teście | iloczyn kartezjański kombinacji (3×2 = 6 testów) |
| `ids=[...]` | własne nazwy przypadków w raporcie |
| `parametrize` + `pytest.raises` | wiele danych błędnych, ten sam wyjątek |

**Parametryzacja fixture:**

```python
@pytest.fixture(params=[1, 2, 3])
def liczba(request):
    return request.param
```

---

## 9. Markery

| Marker | Działanie | Status w raporcie |
|---|---|---|
| `@pytest.mark.skip(reason="...")` | zawsze pomija | SKIPPED |
| `@pytest.mark.skipif(warunek, reason="...")` | pomija warunkowo | SKIPPED |
| `@pytest.mark.xfail(reason="...")` | oczekiwana porażka | XFAIL / XPASS |
| `@pytest.mark.xfail(strict=True)` | nieoczekiwany sukces = błąd | FAILED |
| `@pytest.mark.nazwa` | własny marker | — |

```python
import sys

@pytest.mark.skipif(sys.version_info < (3, 10), reason="wymaga Pythona 3.10+")
def test_nowa_skladnia():
    ...

@pytest.mark.smoke
def test_logowanie():
    ...
```

**Rejestracja własnych markerów** (bez tego: ostrzeżenie `unknown marker`):

```ini
[pytest]
markers =
    smoke: szybkie testy podstawowe
    slow: testy trwające długo
```

Uruchomienie: `pytest -m smoke`

---

## 10. setup / teardown (klasyczne)

| Metoda | Kiedy |
|---|---|
| `setup_function` / `teardown_function` | przed/po każdej funkcji testowej |
| `setup_method` / `teardown_method` | przed/po każdej metodzie w klasie |
| `setup_class` / `teardown_class` | raz na klasę |
| `setup_module` / `teardown_module` | raz na plik |

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

Kolejność dla klasy z dwoma testami:
`setup_class` → `setup_method` → test 1 → `teardown_method` → `setup_method` → test 2 → `teardown_method` → `teardown_class`

**Fixtures zamiast setup/teardown:** parametryzacja, różny scope, jawne zależności.

---

## 11. Mockowanie

| Narzędzie | Zastosowanie |
|---|---|
| `monkeypatch` (wbudowany) | podmiana atrybutów, funkcji, zmiennych środowiskowych; automatyczny rollback |
| `unittest.mock.patch` / `MagicMock` | podmiana obiektów + sprawdzanie wywołań |
| `pytest-mock` (`mocker`) | wygodny interfejs do `unittest.mock` |

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

| Metoda / atrybut | Sprawdza |
|---|---|
| `assert_called_once()` | wywołanie dokładnie raz |
| `assert_called_with(...)` | ostatnie wywołanie z argumentami |
| `call_count` | liczba wywołań |

---

## 12. Raportowanie wyników

| Opcja | Działanie |
|---|---|
| `--junitxml=report.xml` | raport JUnit XML (dla CI) |
| `--html=report.html --self-contained-html` | raport HTML (`pip install pytest-html`) |
| `--durations=N` | N najwolniejszych testów |
| `-s` | pokazuje `print()` |
| `-v` / `-q` | więcej / mniej szczegółów |

---

## 13. Filtrowanie testów

| Komenda | Działanie |
|---|---|
| `pytest -k "wyrazenie"` | testy po nazwie (`and`, `or`, `not`) |
| `pytest -m nazwa` | testy z markerem |
| `pytest -m "a or b"` | testy z jednym z markerów |
| `pytest plik.py::Klasa::test_metoda` | konkretny test (node id) |
| `pytest --collect-only` | lista testów bez uruchamiania |
| `pytest --lf` | tylko ostatnio nieudane |
| `pytest --ff` | nieudane najpierw, potem reszta |

Przykład: `pytest -k "logowanie and not admin"`

---

## 14. Organizacja projektu i konfiguracja

**pyproject.toml:**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
markers = [
    "smoke: szybkie testy podstawowe",
    "slow: testy trwające długo",
]
```

| Opcja | Znaczenie |
|---|---|
| `testpaths` | gdzie szukać testów |
| `addopts` | opcje dodawane do każdego uruchomienia |
| `markers` | rejestracja markerów (`pytest --markers` pokazuje listę) |

- Gdy istnieje `pytest.ini`, ma pierwszeństwo przed `pyproject.toml`.

```
projekt/
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

| Element `Response` | Zawartość |
|---|---|
| `.status_code` | kod HTTP |
| `.json()` | treść jako dict/list |
| `.text` | treść jako tekst |
| `.headers` | nagłówki |

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

| Metoda HTTP | Przykład | Typowy status |
|---|---|---|
| GET | `requests.get(url)` | 200 |
| POST | `requests.post(url, json={...})` | 201 |
| PUT / PATCH | `requests.put(url, json={...})` | 200 |
| DELETE | `requests.delete(url)` | 200 / 204 |
| nieistniejący zasób | — | 404 |

---

## 16. Testy API — techniki

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

| Technika | Zastosowanie |
|---|---|
| `parametrize` | wiele endpointów / przypadków |
| `isinstance` | walidacja typów pól JSON |
| `timeout=` | ochrona przed zawieszeniem testu |
| fixture z `BASE_URL` | jedno miejsce na adres bazowy |

---

## 17. Sesja, autoryzacja i dane testowe

**Sesja z tokenem:**

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

- `requests.Session()` trzyma nagłówki i cookies między requestami.
- `scope="session"` — logowanie/token przygotowany raz na cały przebieg.

**Dane testowe z JSON:**

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

Plik: `.github/workflows/tests.yml`

```yaml
name: Testy pytest

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
          name: raport-testow
          path: report.xml
```

| Element | Znaczenie |
|---|---|
| `on:` | wyzwalacze (push, pull_request) |
| `actions/checkout` | pobranie kodu |
| `actions/setup-python` | wybór wersji Pythona |
| `run:` | komenda w shellu |
| `upload-artifact` | zapis raportu jako artefakt |

Uruchomienie tylko smoke na PR: `pytest -m smoke`
