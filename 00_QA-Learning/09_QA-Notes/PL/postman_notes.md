# Postman — Notes

## 00. Podstawowa zasada — zawsze zapisuj request

Po utworzeniu lub zmodyfikowaniu requestu kliknij **Save** i upewnij się, że zapisał się w odpowiedniej kolekcji. Niezapisane requesty mogą zniknąć po odświeżeniu Postmana albo nie działać poprawnie w Collection Runnerze.

**Schemat:**
```
Create → Configure → Save → <nazwa kolekcji>
```

---

## 01. HTTP Methods

| Metoda | Do czego służy | Przykład |
|---|---|---|
| `GET` | Pobieranie danych | Pobierz użytkownika |
| `POST` | Tworzenie danych | Utwórz użytkownika |
| `PUT` | Pełna aktualizacja zasobu | Zaktualizuj użytkownika |
| `PATCH` | Częściowa aktualizacja | Zmień tylko email |
| `DELETE` | Usuwanie danych | Usuń użytkownika |
| `HEAD` | Pobiera informacje z nagłówków bez body | Sprawdź, czy zasób istnieje |
| `OPTIONS` | Sprawdzenie dostępnych metod/opcji | Sprawdź, jakie metody obsługuje endpoint |

> **Ważne:** JSONPlaceholder jest testowym/mockowym API. Dlatego niektóre operacje, np. `POST`/`PUT`/`PATCH`/`DELETE`, nie zapisują rzeczywistych zmian w trwałej bazie danych.

---

## 02. HTTP Status Codes — kody odpowiedzi HTTP

| Kod | Nazwa | Znaczenie |
|---|---|---|
| 🟢 200 | OK | Żądanie wykonane poprawnie |
| 🟢 201 | Created | Utworzono nowy zasób |
| 🟢 204 | No Content | Sukces, ale brak treści odpowiedzi |
| 🔵 301 | Moved Permanently | Zasób został trwale przeniesiony |
| 🔵 302 | Found | Tymczasowe przekierowanie |
| 🔴 400 | Bad Request | Nieprawidłowe żądanie |
| 🔴 401 | Unauthorized | Brak poprawnego uwierzytelnienia |
| 🔴 403 | Forbidden | Brak uprawnień |
| 🔴 404 | Not Found | Nie znaleziono zasobu |
| 🔴 405 | Method Not Allowed | Metoda HTTP niedozwolona |
| 🔴 409 | Conflict | Konflikt z aktualnym stanem zasobu |
| 🔴 422 | Unprocessable Content | Dane są nieprawidłowe logicznie |
| ⚫ 500 | Internal Server Error | Wewnętrzny błąd serwera |
| ⚫ 502 | Bad Gateway | Problem z serwerem pośredniczącym |
| ⚫ 503 | Service Unavailable | Serwer chwilowo niedostępny |
| ⚫ 504 | Gateway Timeout | Przekroczono czas oczekiwania na odpowiedź |

**Zakresy kodów:**

| Zakres | Znaczenie |
|---|---|
| 2xx | ✅ Sukces |
| 3xx | 🔄 Przekierowanie |
| 4xx | ❌ Błąd klienta |
| 5xx | 💥 Błąd serwera |

---

## 03. Parameters

### 1. Path Parameters
Parametr znajduje się w ścieżce URL i wskazuje konkretny zasób.
```
GET /users/5
```
`5` → ID użytkownika.

> Path Parameter = konkretny zasób

### 2. Query Parameters
Parametr znajduje się po `?` i przekazuje dodatkowe informacje do API.
```
GET /posts?userId=1
```

| Przykład | Zastosowanie |
|---|---|
| `?userId=1` | filtrowanie |
| `?search=test` | wyszukiwanie |
| `?limit=10` | ograniczenie wyników |
| `?page=2` | wybór strony |
| `?sort=name` | sortowanie |

> Query Parameter = filtr / opcja / dodatkowe kryterium

### 3. Multiple Query Parameters
Można używać wielu parametrów jednocześnie, oddzielając je znakiem `&`.
```
GET /posts?userId=1&id=5
```

### 4. Pagination
Dzielenie dużej liczby wyników na strony.
```
GET /posts?_page=2&_limit=5
```

| Parametr | Znaczenie |
|---|---|
| `_page=2` | druga strona |
| `_limit=5` | maks. 5 wyników |

> API nie przechodzi automatycznie na kolejną stronę — aplikacja musi wysłać kolejny request.

### 5. Filtering
Najczęściej realizowane przez Query Parameters.
```
GET /posts?userId=1
```
→ zwraca posty użytkownika 1.

### 6. Sorting
```
GET /users?sort=name&order=asc
```
→ sortowanie po nazwie rosnąco. Nazwy parametrów zależą od konkretnego API.

### Path vs Query

| Path | Query |
|---|---|
| `/users/5` | `/users?id=5` |
| konkretny zasób | dodatkowe kryterium |
| część ścieżki | po `?` |

---

## 04. Headers & Body

**Headers** — dodatkowe informacje przesyłane z requestem, np. format danych lub autoryzacja.

**Content-Type** — określa format danych w Body.
```
Content-Type: application/json
```

**Body** — dane przesyłane do API, np. przy `POST`, `PUT`, `PATCH`.
```json
{
  "name": "Test User",
  "email": "test@example.com"
}
```

**Request** → Method, URL, Headers, Body
**Response** → Status Code, Headers, Body

---

## 05. Authentication

**Authentication** — proces sprawdzania, czy klient ma prawo uzyskać dostęp do API.

### Bearer Token / JWT
Token otrzymany po zalogowaniu jest wysyłany w Headerze:
```
Authorization: Bearer <token>
```

| Przypadek | Rezultat |
|---|---|
| Brak tokena | 401 Unauthorized |
| Błędny token | 401 Unauthorized |
| Poprawny token | 200 OK |

### API Key
Klucz używany do identyfikacji/uwierzytelnienia klienta. Może być przekazywany np. jako:
```
X-API-Key: <key>
```
lub jako Query Parameter:
```
?api_key=<key>
```

### Basic Auth
Uwierzytelnianie za pomocą:
```
Username + Password
```
Postman wysyła:
```
Authorization: Basic <credentials>
```

> Basic Auth nie szyfruje danych — powinien być używany z HTTPS.

---

## 06. Variables

**Variables** — przechowują wartości używane wielokrotnie w requestach.

### Podstawowe zastosowanie
```
{{baseUrl}}/users
{{accessToken}}
{{userId}}
```

**Przykład:**

| Variable | Value |
|---|---|
| `baseUrl` | `https://api.example.com` |
| `accessToken` | `eyJ...` |

Zamiast wpisywać pełny URL:
```
https://api.example.com/users
```
używamy:
```
{{baseUrl}}/users
```

### Token
Token można przechowywać jako zmienną:
```
accessToken = eyJ...
```
i używać:
```
Authorization: Bearer {{accessToken}}
```
Dzięki temu zmieniamy token tylko w jednym miejscu.

**Najważniejsze:** `{{variable}}` — sposób odwołania do zmiennej w Postmanie.

Variables można wykorzystywać m.in. w:
- URL
- Headers
- Authorization
- Body

---

## 07. Postman API Testing Cookbook

Testy w Postmanie służą do automatycznego sprawdzania odpowiedzi API.

| # | Test | Co sprawdza | Przykład |
|---|---|---|---|
| 01 | Status Code | Czy API zwróciło oczekiwany kod HTTP | 200, 201, 404 |
| 02 | Response Body | Czy odpowiedź zawiera oczekiwane dane | `json.id` istnieje |
| 03 | Field Value | Czy pole ma konkretną wartość | `id = 1` |
| 04 | Data Type | Czy pole ma właściwy typ danych | `id` → number |
| 05 | Response Time | Czy API odpowiada wystarczająco szybko | < 1000 ms |
| 06 | Headers | Czy odpowiedź zawiera wymagane nagłówki | `Content-Type` |
| 07 | JSON Structure | Czy odpowiedź ma oczekiwaną strukturę | `id`, `name`, `email` |
| 08 | Array Is Not Empty | Czy zwrócona tablica zawiera dane | `[]` → FAIL |
| 09 | Array Element Exists | Czy element tablicy zawiera wymagane pole | `json[0].id` |
| 10 | Required Fields | Czy wszystkie wymagane pola istnieją | `id`, `name`, `email` |
| 11 | Empty / Null | Czy wymagane pole nie jest puste / null | `email` |
| 12 | String Validation | Czy wartość jest tekstem | `name` → string |
| 13 | Number Validation | Czy wartość jest liczbą | `id` → number |
| 14 | Boolean Validation | Czy wartość to true / false | `active` → boolean |
| 15 | Authentication | Czy API prawidłowo obsługuje autoryzację | 200 / 401 |
| 16 | Negative Test | Czy API prawidłowo odrzuca niepoprawne żądanie | 400, 401, 404 |
| 17 | Error Response | Czy błąd ma poprawną strukturę | `error.code`, `message` |
| 18 | POST Validation | Czy utworzenie zasobu zakończyło się poprawnie | 201 Created |
| 19 | PUT/PATCH Validation | Czy aktualizacja zasobu zakończyła się poprawnie | 200 / 204 |
| 20 | DELETE Validation | Czy usunięcie zasobu zakończyło się poprawnie | 200 / 204 |
| 21 | Combined Test | Kilka niezależnych sprawdzeń jednej odpowiedzi | status + body + fields + czas |

### Najczęściej używane schematy

```js
const json = pm.response.json();
```
Pobiera Response Body jako JSON.

```js
pm.expect(json.id).to.exist;
```
Sprawdza, czy pole istnieje.

```js
pm.expect(json.id).to.eql(1);
```
Sprawdza konkretną wartość.

```js
pm.expect(json.id).to.be.a("number");
```
Sprawdza typ danych.

```js
pm.response.to.have.status(200);
```
Sprawdza status HTTP.

> **Najważniejsza zasada:** test nie ma tylko potwierdzać, że request „działa”. Ma sprawdzać, czy rzeczywista odpowiedź jest zgodna z oczekiwaniem/specyfikacją.

---

## 08. Scripts

Skrypty w Postmanie służą głównie do automatyzacji pracy z requestami i odpowiedziami API.

| # | Temat | Zastosowanie | Schemat |
|---|---|---|---|
| 01 | Response → Variable | Pobranie wartości z odpowiedzi i zapisanie jej jako Variable | Response → Script → Variable |
| 02 | Variable → Request | Użycie zapisanej wartości w kolejnym requestcie | `{{variable}}` |
| 03 | Simple If Logic | Wykonanie kodu tylko po spełnieniu warunku | `if (condition) { ... }` |
| 04 | Iterate Through Array | Wykonanie operacji dla każdego elementu tablicy | `array.forEach(...)` |
| 05 | Debugging with console.log() | Podejrzenie wartości podczas działania skryptu | `console.log(value)` |

Skrypty dzielą się na dwa główne rodzaje, w zależności od momentu wykonania (patrz też sekcja 14):

- **Pre-request Script** — wykonuje się **przed** wysłaniem requestu
- **Post-request / Test Script** — wykonuje się **po** otrzymaniu response

Do pracy ze skryptami służy globalny obiekt `pm` (patrz sekcja 14).

---

## 09. Collection Runner

Collection Runner pozwala uruchomić wiele requestów z jednej kolekcji automatycznie, zamiast wysyłać je pojedynczo. Każdy request może mieć własne testy, a Runner pokazuje wynik **PASS / FAIL** dla każdego z nich.

`Iterations` określa, ile razy cała kolekcja zostanie wykonana.

> **Ważne:** requesty muszą być zapisane w kolekcji, inaczej Runner może nie widzieć ich URL-i i nie wykona ich poprawnie.

**Schemat:**
```
Collection → Runner → Requests → Tests → PASS / FAIL
```

Runner potrafi dodatkowo:
- uruchomić całą kolekcję sekwencyjnie,
- zachowywać zmienne między requestami (np. token zapisany w request #1 jest dostępny w request #5),
- uruchamiać testy wielokrotnie (`Iterations`),
- planować uruchomienia (scheduled runs).

> **Collection Runner ≠ CLI.** Runner jest do interaktywnego uruchamiania/debugowania wewnątrz aplikacji Postman. Postman CLI jest potrzebny, gdy testy mają działać bez otwartego Postmana — np. w CI/CD (patrz sekcja 21).

---

## 10. Workspaces

**Workspace** — przestrzeń do organizowania pracy związanej z API.

Może zawierać m.in.: **collections, environments, monitors, mock servers i documentation**.

**Typy workspace:**

| Typ | Znaczenie |
|---|---|
| Internal | dla zespołu |
| Partner | dla zaproszonych partnerów |
| Public | dostępny publicznie |

Typ workspace można zmienić w: **Workspace Overview → Settings**.

W ramach workspace/projektu można współpracować przez komentarze (patrz sekcja 12).

---

## 11. Collections — rozszerzenie

**Collection** = grupa powiązanych requestów API wraz ze skryptami, zmiennymi, dokumentacją i przykładami.

Najważniejsze zastosowania:
- organizowanie requestów,
- przechowywanie **testów i skryptów**,
- dokumentacja,
- automatyzacja przez **Collection Runner**,
- współdzielenie i wersjonowanie.

**Dobra praktyka:** organizować requesty według **zasobów** (np. *Users*, *Tasks*, *Books*), a nie według metody HTTP — patrz sekcja 28 (organizacja kolekcji według domeny).

---

## 12. Environments & Variable Scopes

Environment pozwala przechowywać zmienne używane w wielu requestach, np. zamiast:
```
https://api.example.com
```
używasz:
```
{{baseUrl}}
```

Dzięki temu można przełączać się np. między **development / staging / production** bez edytowania requestów.

### Scopes zmiennych — od najszerszego do najwęższego

1. **Global**
2. **Environment**
3. **Collection**
4. **Local**

> **Ważne:** węższy scope może nadpisać zmienną o tej samej nazwie z szerszego scope.

`{{variable}}` → Postman podstawia wartość zmiennej podczas wykonywania requestu.

> **Uwaga na nazewnictwo:** `baseURL` i `baseUrl` to **dwie różne zmienne** — wielkość liter ma znaczenie.

---

## 13. Mock Servers

**Mock Server** pozwala **udawać działające API**, zwracając wcześniej przygotowane odpowiedzi — backend nie musi jeszcze istnieć.

Mock korzysta z zapisanych w Collection **Example Responses**, które definiują:
- method,
- path,
- status code,
- headers,
- body.

**Typowe zastosowanie:** frontend może być testowany, zanim backend będzie gotowy.

URL mock servera można ustawić jako wartość zmiennej środowiskowej (np. `baseURL`), dzięki czemu ta sama kolekcja requestów może być wykonywana zarówno na mocku, jak i na prawdziwym API.

---

## 14. Testing Scripts — pm, pre-request i post-request

Postman pozwala używać **JavaScript** do automatyzacji requestów i testowania odpowiedzi. Do pracy z Postmanem służy globalny obiekt **`pm`**.

### Pre-request Script
- wykonuje się **przed** wysłaniem requestu
- typowe zastosowanie: przygotowanie danych, ustawienie zmiennej, wygenerowanie dynamicznej wartości

### Post-request Script (Test Script)
- wykonuje się **po** otrzymaniu response
- może m.in.:
  - sprawdzać status code,
  - sprawdzać body,
  - walidować strukturę JSON,
  - wyciągać wartości z response,
  - zapisywać wartość (np. **token**) do zmiennej, żeby wykorzystać ją w kolejnym requestcie.

> Dzięki temu można wykonywać kilkanaście precyzyjnych, powiązanych requestów, zamiast ręcznie tworzyć dziesiątki niemal identycznych testów.

---

## 15. First Project — dobre praktyki organizacji

### Test Scripts w praktyce
- Postman pozwala pisać skrypty JavaScript do automatycznej weryfikacji odpowiedzi.
- Typowy przykład: **post-response script** sprawdzający status code.
- Jeśli test nie przechodzi, warto po kolei sprawdzić:
  1. HTTP method
  2. endpoint URL
  3. oczekiwany status code
  4. status code zapisany w Example Response

### HTTP methods w rozszerzaniu kolekcji
Przy rozbudowie projektu typowo dochodzą kolejne metody: **POST**, **PUT**, **DELETE** (oprócz podstawowego GET).

---

## 16. Collaboration

Postman umożliwia współpracę zespołową bezpośrednio na kolekcjach:
- komentarze dotyczące całej kolekcji/requestu,
- komentarze inline dotyczące konkretnego fragmentu requestu,
- `@mention` innych członków zespołu,
- odpowiadanie w wątku i oznaczanie komentarzy jako rozwiązanych.

---

## 17. API Testing — zakres jakości

API testing nie ogranicza się do sprawdzenia, czy endpoint zwraca poprawne dane. Obejmuje m.in.:

| Obszar | Co sprawdza |
|---|---|
| **Functionality** | czy API działa zgodnie z wymaganiami |
| **Reliability** | czy zachowuje się stabilnie |
| **Performance** | response time, throughput, zachowanie pod obciążeniem |
| **Security** | autoryzacja, podatności, ekspozycja danych |

### Różne role → różne cele testowania

| Rola | Cel testowania |
|---|---|
| Developer | poprawność pojedynczych endpointów |
| QA | zachowanie end-to-end + regresja |
| Automation Engineer | powtarzalne testy w CI/CD |
| Security | podatności, konfiguracja, data exposure |
| Performance Engineer | response time, throughput, load |
| API Designer/Architect | spójność i poprawność kontraktu |
| Product Owner | zgodność z wymaganiami produktu |

> API testing jest więc **cross-functional**, a nie wyłącznie domeną QA.

---

## 18. Obszary, które API testing powinien pokrywać

### Rate limiting
Sprawdzamy:
- limity requestów,
- `429 Too Many Requests`,
- nagłówek `Retry-After`.

### Response accuracy
Czy response zawiera:
- poprawne wartości,
- poprawne obliczenia,
- prawidłowe zależności między danymi.

### Data validation
API powinno walidować:
- required fields,
- typy danych,
- min/max,
- format,
- enum values.

> Przykład testowany na DummyJSON: `price: "free"`, `age: "twenty"`, `quantity: -1` — czyli wartości niepoprawne typologicznie/logicznie, które API powinno odrzucić lub obsłużyć poprawnie.

### Response time
Testujemy szybkość odpowiedzi zarówno przy normalnym ruchu, jak i przy większym obciążeniu.

### Edge cases
Przykłady:
- empty arrays,
- `null`,
- bardzo długie stringi,
- maksymalne wartości,
- Unicode,
- concurrent updates (równoczesne aktualizacje tego samego zasobu).

### Response format / schema
Sprawdzamy stabilność:
- JSON schema,
- nazwy pól,
- typy danych,
- pagination structure.

> To jest szczególnie ważne, ponieważ klienci API mogą zależeć od konkretnej struktury odpowiedzi.

---

## 19. Cztery podstawowe rodzaje testów

| Typ testu | Co sprawdza |
|---|---|
| **Unit testing** | mały, izolowany fragment kodu; szybkie i bardzo konkretne testy |
| **Contract testing** | czy API przestrzega ustalonego kontraktu (struktury request/response) |
| **End-to-end testing** | cały przepływ przez kilka elementów/systemów |
| **Load testing** | zachowanie API pod dużym obciążeniem |

> Nie każdy test trzeba robić na każdym poziomie — typ testu dobiera się do celu.

---

## 20. API Test Automation

Automatyzacja API = testy wykonywane automatycznie za pomocą narzędzi/skryptów zamiast ręcznego uruchamiania każdego przypadku.

### Dlaczego automatyzujemy?

1. **Mniej ręcznej pracy** — szczególnie przy regression testing
2. **Consistency** — za każdym razem wykonywane są dokładnie te same sprawdzenia
3. **CI/CD** — testy mogą być uruchamiane automatycznie po zmianach w kodzie i blokować wadliwy kod przed wdrożeniem

### 4 główne korzyści automatyzacji (szerzej)

- **Speed** — setki testów w krótkim czasie
- **Consistency** — te same testy wykonywane zawsze tak samo
- **Early detection** — szybkie wykrywanie regresji
- **Coverage** — łatwiejsze testowanie wielu danych i kombinacji

> **Manual → Automation:** automatyzacja nie zastępuje QA. Automatyzuje powtarzalne wykonywanie testów, a QA nadal odpowiada za projektowanie testów, interpretację wyników i dobór scenariuszy.

---

## 21. Typowy pipeline API testing

```
Developer writes code
        ↓
   Commit / Push
        ↓
  CI triggers tests
        ↓
     Unit tests
        ↓
Contract / Integration / E2E tests
        ↓
 Performance / Load tests
        ↓
       Deploy
        ↓
Smoke tests + monitoring
```

Ten przepływ pokazuje pełny cykl: unit tests przy developmencie → CI po pushu → integration/contract/E2E na staging → performance/load → deployment → smoke testing i monitoring na produkcji.

---

## 22. Generowanie kolekcji z OpenAPI

Zamiast ręcznie tworzyć kilkadziesiąt requestów, można zaimportować **OpenAPI/Swagger YAML** — Postman wygeneruje kolekcję na podstawie specyfikacji. Specyfikacja opisuje m.in. endpointy, metody, parametry i schematy odpowiedzi.

---

## 23. Fork kolekcji

Jeżeli istnieje kolekcja będąca źródłem/referencją, tworzy się **fork** do własnych testów zamiast modyfikować oryginał.

```
Original collection → Fork → własne testy
```

Dzięki temu można rozwijać testową wersję niezależnie od źródłowej.

---

## 24. Collection-level vs Request-level tests

To jedno z kluczowych rozróżnień w projektowaniu test suite.

### Collection / Folder level
Test wspólny dla wielu requestów, np.:
```
status === 200
response time < 2000 ms
Content-Type === application/json
```
Nie trzeba go kopiować do każdego requestu osobno.

### Request level
Test dotyczący konkretnego endpointu, np. `/weather/{airportCode}` musi zwrócić:
```
temperature
wind
visibility
```

### Zasada

> **Wspólne → collection/folder. Specyficzne → request.**

To podejście **DRY — Don't Repeat Yourself**, bardzo przydatne przy budowaniu realnego test suite, a nie tylko pojedynczych requestów.

---

## 25. False Positives

**Test przechodzący ≠ dobry test.** Trzeba sprawdzić, czy test faktycznie wykryje problem.

Dobre praktyki:
- analizowanie przyczyn failure,
- sprawdzanie zależności między danymi,
- odpowiednie chainowanie requestów,
- **celowe zepsucie czegoś i sprawdzenie, czy test upadnie**.

```
Test powinien PASS
        ↓
celowo zmieniam oczekiwaną wartość
        ↓
test powinien FAIL
        ↓
jeżeli nadal PASS → test jest zły
```

> **Najważniejszy meta-wzorzec:** test powinien być w stanie wykryć błąd, a nie tylko przejść.

---

## 26. Postman Snippets

Postman ma bibliotekę gotowych fragmentów testów — można z niej szybko dodać np.:
- status code,
- response time,
- JSON schema,
- headers.

> **Ważne:** snippet to tylko punkt startowy. Trzeba dostosować asercję do faktycznego kontraktu API.

---

## 27. Agent Mode

Postman może wygenerować testy na podstawie odpowiedzi API.

```
Agent
  ↓
generuje test
  ↓
QA review
  ↓
poprawa
  ↓
weryfikacja
  ↓
dopiero wtedy test jest wartościowy
```

> Agent generuje **pierwszy szkic**, a QA musi go sprawdzić. Nie należy bezmyślnie wrzucać wygenerowanych testów do kolekcji.

---

## 28. Error Handling — testowanie błędów

Testuj nie tylko happy path — celowo wywołuj błędy (np. 404, 401, 403, 500).

Dla każdego testowanego błędu sprawdzaj ten sam zestaw elementów:
```
status → Content-Type → wymagane nagłówki → body/schema → konkretny komunikat
```

Sprawdzaj:
- status code,
- Content-Type,
- wymagane nagłówki,
- strukturę body błędu,
- czy komunikat błędu jest użyteczny.

**RFC 7807** → standardowy format odpowiedzi błędów: `application/problem+json`.

### Przykładowy wzorzec testu błędu

```js
pm.test("Status code is 404", () => {
    pm.response.to.have.status(404);
});

pm.test("Content-Type is problem+json", () => {
    pm.expect(pm.response.headers.get("Content-Type"))
        .to.include("application/problem+json");
});

pm.test("Correlation ID exists", () => {
    pm.response.to.have.header("x-correlation-id");
});
```

Ten sam schemat działa dla różnych kodów błędów (404, 401, 403, 500) — zmienia się głównie oczekiwany status i szczegóły błędu, co pozwala ograniczyć duplikację testów.

---

## 29. Data Validation Pattern

Sam `200 OK` nie oznacza, że odpowiedź jest poprawna. Jeden test może sprawdzać kilka aspektów kontraktu odpowiedzi naraz:
```
required field + format + enum + data type
```

```js
pm.expect(data).to.have.property("airportCode");
pm.expect(data.airportCode).to.match(/^[A-Z]{4}$/);
pm.expect(data.status).to.be.oneOf(["active", "closed"]);
pm.expect(data.temperature).to.be.a("number");
```

Waliduj:
- required fields,
- data types,
- formaty,
- zakresy,
- enum / dozwolone wartości.

---

## 30. skipTest Pattern

Jeżeli request zwróci nieoczekiwane `404`, testy walidujące body mogą zostać pominięte zamiast generować fałszywy FAIL.

```js
if (pm.response.code === 404) {
    console.warn("Skipping validation — test data unavailable");
} else {
    // validation tests
}
```

Schemat decyzyjny:
```
request
   ↓
  404?
 ├── TAK → pomiń validation
 └── NIE → wykonaj validation
```

> **Nie stosować tego do testów, których celem jest właśnie sprawdzenie 404** — wtedy chcesz, żeby test faktycznie zweryfikował ten kod błędu, a nie go pominął.

---

## 31. Performance Testing w Postmanie

- `pm.response.responseTime` → czas odpowiedzi
- `pm.response.size` → rozmiar odpowiedzi

```js
pm.test("Response time is below 500 ms", () => {
    pm.expect(pm.response.responseTime).to.be.below(500);
});
```

Szerszy wzorzec oceny wydajności:
```
response time + response size + wiele iteracji + analiza wyniku
```

**Zasady:**
- Nie oceniaj wydajności na podstawie pojedynczego requestu — pojedynczy spike może wynikać np. z sieci.
- Przy większej liczbie iteracji można analizować wzorzec, np. czy 95% odpowiedzi mieści się w określonym progu.
- Collection Runner może być użyty do uruchamiania wielu iteracji / symulowania wielu użytkowników.

---

## 32. Data-Driven Testing

Zamiast pisać osobny test dla każdego przypadku:
```
test 1 → airport = WAW
test 2 → airport = LHR
test 3 → airport = JFK
test 4 → airport = CDG
```

robi się:
```
JEDEN TEST
    ↓
  CSV / JSON
    ↓
 wiele danych
    ↓
wiele iteracji
```

Postman wykonuje tę samą kolekcję dla każdego wiersza danych z pliku.

> **Write tests once, add scenarios by adding data.**

**Dobra praktyka:** nie twórz od razu 500 przypadków testowych. Zacznij od **5–10 reprezentatywnych przypadków → uruchomienie → analiza → rozszerzanie danych**.

---

## 33. Postman CLI i CI/CD

```
Postman Collection
        ↓
    Postman CLI
        ↓
  GitHub Actions
        ↓
 testy automatyczne
        ↓
PASS → dalej
FAIL → pipeline może się zatrzymać
```

Postman CLI wykonuje **te same kolekcje i testy**, które zostały stworzone w aplikacji Postman — nie tworzy się osobnego zestawu testów specjalnie dla CLI.

### Collection Runner vs CLI vs Postman API

| Narzędzie | Zastosowanie |
|---|---|
| **Collection Runner** | Uruchamianie i debugowanie testów w Postmanie |
| **Data files** | Testowanie wielu scenariuszy na różnych danych |
| **Postman CLI** | Uruchamianie kolekcji z terminala / CI/CD |
| **Postman API** | Programowe zarządzanie zasobami Postmana |

> **Najważniejsze rozróżnienie:** CLI uruchamia testy. API Postmana zarządza Postmanem.

### Postman API
Pozwala programowo zarządzać m.in.:
- Workspaces,
- Collections,
- Environments,
- Monitors,
- dostępem/rolami.

Dzięki temu można zautomatyzować nawet **przygotowanie środowiska testowego**, a nie tylko samo wykonywanie testów.

### Obraz całego modułu automatyzacji
```
1. Collection Runner
        ↓
2. Data-driven testing
        ↓
3. Postman CLI
        ↓
4. Postman API
        ↓
5. CI/CD
```

> **Automatyzacja daje szybkość, ale nie daje automatycznie dobrych testów.** Jeżeli założenia testów są złe albo dokumentacja nieaktualna, automatyzacja po prostu szybciej produkuje błędne wyniki.

---

## 34. Reusable / Modular Tests

Zamiast kopiować tę samą funkcję walidacyjną do wielu requestów:
```
❌ Request A → własna walidacja
❌ Request B → skopiowana walidacja
❌ Request C → skopiowana walidacja
```

buduje się wspólną bibliotekę:
```
Biblioteka pakietów
        ↓
wspólne funkcje walidacyjne
   ↙     ↓     ↘
Request A  Request B  Request C
```

Czyli: **napisz raz → używaj wszędzie**.

### module.exports jako publiczny kontrakt

```js
module.exports = {
    validateMetar,
    validateWindData
}
```

Eksporty należy traktować jak **publiczne API**:

| Zmiana | Bezpieczna? |
|---|---|
| dodanie nowej funkcji | ✅ bezpieczne |
| dodanie opcjonalnego parametru | ✅ bezpieczne |
| poprawienie błędu (bugfix) | ✅ bezpieczne |
| zmiana nazwy funkcji | ❌ breaking change |
| usunięcie funkcji | ❌ breaking change |
| zmiana formatu zwracanych danych | ❌ breaking change |

### Spójny format zwracanych danych

Każda funkcja walidacyjna powinna zwracać dane w tym samym, spójnym formacie, np.:
```js
{
    valid: true,
    error: null
}
```

Dzięki temu można łączyć wiele walidatorów w jeden pipeline:
```
validateMetar()
validateWindData()
validateVisibility()
validateTemperature()
        ↓
ten sam format wyniku
        ↓
łatwe połączenie w jeden pipeline
```

> **Jednolity output = łatwe komponowanie testów.**

### pm.require() — import wspólnej logiki

Zamiast kopiować kod między requestami:
```js
const { validateMetar } = pm.require('@postair/metar-validators');
```

To odpowiada myśleniu: **Biblioteka → import → test**, a nie **Biblioteka → kopiuj kod → wklej → kopiuj → wklej**.

---

## 35. Chained / Dependent Requests

Request #1 zwraca dane, których używa Request #2:
```
GET /airports
       ↓
  airportCode
       ↓
GET /metars/{{airportCode}}
       ↓
GET /forecast/{{airportCode}}
```

Zamiast wpisywać wartość na sztywno (np. `ATL`), pobiera się ją dynamicznie z poprzedniego requestu i zapisuje jako zmienną (np. w Test Script przez `pm.environment.set(...)` / `pm.collectionVariables.set(...)`).

---

## 36. Environment-Driven Testing

Rzeczy zależne od środowiska **nie powinny być wpisane bezpośrednio w request**.

**❌ Źle:**
```
https://test-api.example.com
API_KEY=123456
```

**✅ Dobrze:**
```
{{baseUrl}}
{{apiKey}}
```

Środowisko decyduje, jakie wartości faktycznie zostaną podstawione:
```
Test environment
      ↓
{{baseUrl}} = test-api...

Production
      ↓
{{baseUrl}} = api...
```

Dzięki temu **ta sama kolekcja może działać w różnych środowiskach** bez ręcznej edycji requestów.

---

## 37. Organizacja kolekcji według domeny

**Nie** rób jako głównego podziału kolekcji:
```
GET
POST
PUT
DELETE
```

**Lepiej** grupować według funkcjonalności/domeny API:
```
📁 Airports
   ├── Get airports
   └── Get airport

📁 Weather
   ├── Get forecast
   └── Get METAR

📁 Reports
   └── ...
```

> Grupuj według funkcjonalności/domeny API, nie według metody HTTP.

---

## 38. Setup → Test → Teardown

```
SETUP
   ↓
przygotuj token / dane testowe
   ↓
TEST
   ↓
wykonaj requesty + asercje
   ↓
TEARDOWN
   ↓
posprzątaj dane
```

Dzięki takiej strukturze folder/test jest bardziej samodzielny i bezpieczny do wielokrotnego, powtarzalnego uruchamiania (np. w CI/CD, gdzie dane testowe nie powinny się kumulować między przebiegami).

---

## 39. Uzupełnienie — standardowe elementy Postmana (prawdopodobnie pokazane na filmie, nieujęte w tekście notatek)

Poniższe elementy to standardowe funkcje platformy Postman, które zwykle pojawiają się w praktycznej części kursu (pokazywane na ekranie), ale nie zawsze trafiają do notatek tekstowych. Warto je znać jako uzupełnienie powyższych wzorców:

### Postman Console
Narzędzie do podglądu pełnych requestów i response'ów (surowe nagłówki, body, czas wykonania) — pomocne przy debugowaniu, gdy `console.log()` w skrypcie nie wystarcza. Otwierane zwykle jako osobny panel w aplikacji.

### Dynamiczne zmienne wbudowane
Postman udostępnia gotowe zmienne generujące dane w locie, przydatne np. przy testach z losowymi/unikalnymi danymi:
```
{{$guid}}        — losowy UUID
{{$timestamp}}   — aktualny czas Unix
{{$randomEmail}} — losowy adres email
{{$randomInt}}   — losowa liczba całkowita
```

### Zapisywanie zmiennych ze skryptu
```js
pm.environment.set("token", jsonData.token);       // zmienna w bieżącym environment
pm.collectionVariables.set("orderId", jsonData.id); // zmienna na poziomie kolekcji
pm.globals.set("sessionId", jsonData.session);       // zmienna globalna
```
To praktyczna realizacja wzorca chained requests (sekcja 35) — dokładnie w ten sposób zapisuje się wartość z jednej odpowiedzi, żeby użyć jej w kolejnym requestcie.

### Visualizer
Pozwala wyrenderować response (np. JSON) jako czytelny HTML/tabelę wewnątrz Postmana — użyteczne przy przeglądaniu większych odpowiedzi bez kopiowania ich do zewnętrznego narzędzia.

### Monitors
Funkcja umożliwiająca zaplanowane, cykliczne uruchamianie kolekcji (np. co godzinę) bezpośrednio z serwerów Postmana, niezależnie od otwartej aplikacji — używana m.in. do monitorowania dostępności API w czasie.

### Import specyfikacji i generowanie dokumentacji
Poza importem OpenAPI/Swagger (sekcja 22), Postman potrafi też automatycznie wygenerować czytelną **dokumentację kolekcji** (widoczną publicznie lub w zespole) na podstawie zapisanych requestów, przykładów i opisów.

---

## 🧠 Ultra-krótka ściąga — 7 kluczowych wzorców budowy test suite

```
1. Reusable tests        → wspólna logika zamiast kopiowania
2. module.exports         → funkcje jako publiczny kontrakt
3. Consistent output       → { valid, error }
4. pm.require()            → import wspólnych funkcji
5. Chained requests         → wynik A → dane wejściowe B
6. Environment variables     → {{baseUrl}}, {{apiKey}}, {{token}}
7. Setup → Test → Teardown    → przygotuj → testuj → posprzątaj
```

**Najważniejszy obraz całej architektury:**
```
        Postman Package Library
                 ↓
             pm.require()
                 ↓
    ┌────────────┼────────────┐
    ↓            ↓            ↓
Request A    Request B    Request C
    ↓                          ↑
    └──────── dane ────────────┘
                 ↓
            Environment
        {{baseUrl}} {{token}}
```

To już podejście **QA automation / projektowanie frameworka testowego**, a nie tylko klikanie pojedynczych requestów w Postmanie.
