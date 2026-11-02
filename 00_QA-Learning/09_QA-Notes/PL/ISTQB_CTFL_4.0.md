**ISTQB CTFL 4.0 - Notatki własne**

**Źródło: Sylabus ISTQB Certyfikowany Tester — Poziom Podstawowy, wersja 4.0.1 (SJSI) Notatki własne**

** Spis treści:**

1. Podstawy testowania 

2. Testowanie w cyklu wytwarzania oprogramowania 

3. Testowanie statyczne 

4. Analiza i projektowanie testów 

5. Zarządzanie czynnościami testowymi 

6. Narzędzia testowe 

**1. Podstawy testowania. **

**1.1 Kluczowe pojęcia:**

| **Pojęcie** | **Definicja** |
| :-: | :-: |
| **Testowanie** | Zbiór czynności służących wykrywaniu defektów i ocenie jakości produktu pracy. Obejmuje nie tylko wykonywanie testów, ale także planowanie, analizę i projektowanie testów. |
| **Weryfikacja** | Sprawdzenie, czy system został zbudowany zgodnie ze specyfikacją. |
| **Walidacja** | Sprawdzenie, czy system faktycznie odpowiada potrzebom użytkownika. |
| **Testowanie statyczne** | Testowanie bez uruchamiania kodu (np. przeglądy i analiza statyczna). |
| **Testowanie dynamiczne** | Testowanie podczas uruchamiania oprogramowania. |
| **Debugowanie** | Znajdowanie i usuwanie przyczyny awarii: odtworzenie → diagnoza → usunięcie problemu. |
| **Testowanie potwierdzające** | Sprawdzenie po naprawie, czy konkretny defekt został usunięty. |
| **Testowanie regresji** | Sprawdzenie, czy wprowadzone zmiany nie spowodowały nowych problemów w innych obszarach systemu. |
| **Pomyłka** | Błąd człowieka wynikający np. z presji czasu, zmęczenia lub braku wiedzy. |
| **Defekt** | Wada w oprogramowaniu powstała wskutek pomyłki. |
| **Awaria** | Obserwowalne nieprawidłowe działanie systemu spowodowane defektem. |
| **Podstawowa przyczyna (Root Cause)** | Rzeczywista przyczyna problemu, której usunięcie zapobiega jego ponownemu wystąpieniu. |
| **Testalia** | Produkty pracy z testowania (plan testów, przypadki testowe, dane, skrypty, raporty). |
| **Śledzenie powiązań (Traceability)** | Powiązanie wymagań z przypadkami testowymi, wynikami i ryzykami. |


**1.2 Siedem zasad testowania:**

| **Zasada 1 - Testowanie ujawnia defekty** | Znalezienie błędów nie oznacza, że można udowodnić ich całkowity brak. |
| :-: | - |
| **Zasada 2 - Testowanie wyczerpujące jest niemożliwe** | Nie da się sprawdzić wszystkich przypadków, trzeba ustalać priorytety. |
| **Zasada 3 - Wczesne testowanie** | Im wcześniej defekt wykryty, tym tańsza jego naprawa. |
| **Zasada 4 - Kumulowanie się defektów** | Większość defektów zwykle znajduje się w niewielkiej liczbie modułów. |
| **Zasada 5 - Paradoks pestycydów** | Te same testy z czasem przestają wykrywać nowe defekty. |
| **Zasada 6 - Zależność od kontekstu** | Sposób testowania zależy od rodzaju systemu, ryzyka i użytkowników. |
| **Zasada 7 - Przekonanie o braku błędów jest błędem** | Spełnienie wymagań nie oznacza spełnienia rzeczywistych potrzeb. |


**1.3 Proces testowy - czynności (kolejność logiczna, w praktyce iteracyjna):**

- **Monitorowanie i nadzór** - kontrola postępu vs plan

- **Analiza testów** - CO testować (warunki testowe)

- **Projektowanie testów** - JAK testować (przypadki testowe)

- **Implementacja testów** - dane, środowisko, skrypty

- **Wykonywanie testów** - uruchamianie, rejestrowanie wyników

- **Ukończenie testów** - podsumowanie, archiwizacja, raport


**2. Testowanie w cyklu wytwarzania oprogramowania.**

**2.1 Modele SDLC**:

| Model | Charakterystyka |
| :-: | :-: |
| Sekwencyjny | Etapy po kolei (Waterfall, Model V) |
| Iteracyjny | Powtarzające się cykle |
| Przyrostowy | Budowa produktu kawałek po kawałku |
| Agile | Częste dostarczanie, współpraca, akceptowanie zmian |


**2.2 Podejścia "najpierw test":**

| **Podejście** | **Zasada** |
| :-: | :-: |
| **TDD** | **test → kod → refaktoryzacja** |
| **ATDD** | **testy akceptacyjne przed implementacją, na bazie kryteriów akceptacji** |
| **BDD** | **zachowanie opisane zrozumiale dla biznesu, format Given/When/Then** |


**2.3 DevOps i przesunięcie w lewo:**

| **Pojęcie** | **Definicja** |
| :-: | :-: |
| DevOps | Łączenie wytwarzania i operacji, automatyzacja, CI/CD, szybki feedback |
| CI (Continuous Integration) | Częste integrowanie zmian + automatyczne kontrole (np. testy) |
| CD (Continuous Delivery/Deployment) | Automatyzacja dostarczania/wdrażania |
| Przesunięcie w lewo (Shift Left) | Testowanie jak najwcześniej w cyklu wytwarzania |
| Retrospektywa | Spotkanie po iteracji: co działało, co poprawić |


**2.4 Pięć poziomów testów:**

| Poziom | Sprawdza | Kto wykonuje |
| :-: | :-: | :-: |
| Modułowe (jednostkowe) | Pojedyncze moduły w izolacji | programiści |
| Integracji modułów | Interakcje/interfejsy między modułami | programiści |
| Systemowe | Cały system vs wymagania | zespół testowy |
| Integracji systemów | Współpraca z innymi systemami/usługami | zespół testowy |
| Akceptacyjne | Gotowość do wdrożenia, potrzeby biznesowe | biznes/użytkownicy |

**2.5 Typy testów:**

| Typ | Definicja |
| :-: | :-: |
| Funkcjonalne | Sprawdzają CO system robi |
| Niefunkcjonalne | Sprawdzają JAK DOBRZE system działa (wydajność, użyteczność, bezpieczeństwo, kompatybilność) |
| Czarnoskrzynkowe | Bez znajomości wewnętrznej struktury |
| Białoskrzynkowe | Z uwzględnieniem struktury (kod, architektura) |


**2.6 Testowanie potwierdzające vs regresyjne oraz pielęgnacyjne:**

| **Pojęcie** | **Definicja** |
| :-: | :-: |
| Testowanie potwierdzające | Sprawdza KONKRETNY naprawiony defekt |
| Testowanie regresji | Sprawdza czy zmiana nie zepsuła czegokolwiek innego w systemie |
| Testowanie pielęgnacyjne | Po wdrożeniu, wywołane zmianą, migracją lub wycofaniem systemu |
| Analiza wpływu (Impact Analysis) | Poprzedza testowanie pielęgnacyjne - ocena konsekwencji zmiany dla reszty systemu |


**3. Testowanie statyczne.**

**3.1 Podstawy:**

| Pojęcie | Definicja |
| :-: | :-: |
| Testowanie statyczne | Wykrywanie defektów bez uruchamiania oprogramowania |
| Przegląd | Manualna ocena produktu pracy przez ludzi |
| Analiza statyczna | Narzędziowa, automatyczna analiza kodu/struktury |
| Testowanie dynamiczne | Testowanie przez uruchomienie programu |


**Statyczne wykrywa defekty bezpośrednio, dynamiczne wykrywa awarie, które trzeba dopiero zdiagnozować.**

**3.2 Proces przeglądu (kolejność):**

| Etap | Opis |
| :-: | :-: |
| Planowanie | Cel, zakres, kryteria, czas |
| Rozpoczęcie przeglądu | Materiały i role gotowe |
| Przegląd indywidualny | Każdy analizuje samodzielnie |
| Przekazanie informacji i analiza | Omówienie anomalii |
| Usunięcie defektów i raportowanie | Poprawki + dokumentacja |


**3.3 Role w przeglądzie:**

| Rola | Odpowiedzialność |
| :-: | :-: |
| Kierownik | Decyduje co i kiedy przeglądać, zasoby |
| Autor | Stworzył produkt, usuwa defekty |
| Moderator/facylitator | Prowadzi spotkanie |
| Protokolant | Zapisuje anomalie i decyzje |
| Przeglądający | Analizuje produkt |
| Lider przeglądu | Organizacja i ogólny przebieg |


**3.4 Typy przeglądów:**

| Typ | Charakterystyka |
| :-: | :-: |
| Nieformalny | Bez ustalonego procesu |
| Przejrzenie (walkthrough) | Prowadzi autor |
| Techniczny | Osoby z wiedzą techniczną + moderator |
| Inspekcja | Najbardziej formalny, zbiera metryki, autor nie może być liderem ani protokolantem |

**4. Analiza i projektowanie testów.**

**4.1 Techniki czarnoskrzynkowe - 4 najważniejsze:**

| Technika | Na czym polega | Kiedy stosować |
| :-: | :-: | :-: |
| Equivalence Partitioning (klasy równoważności) | Dzielisz dane wejściowe na grupy traktowane tak samo — testujesz 1 wartość z każdej grupy zamiast wszystkich możliwych | Pola z zakresami wartości (np. wiek 18-65) |
| Boundary Value Analysis (wartości brzegowe) | Testujesz wartości na granicach klas — tam najczęściej są błędy programistów | Zawsze razem z equivalence partitioning |
| Tablica decyzyjna | Testujesz wszystkie kombinacje warunków i wynikających z nich akcji | Złożone reguły biznesowe (np. rabaty, uprawnienia) |
| Testowanie przejść między stanami | Modelujesz system jako stany + zdarzenia powodujące przejścia | System z wyraźnymi stanami (np. status zamówienia, logowanie) |


**4.2 Boundary Value Analysis - dwa warianty:**

| Wariant | Co testujesz |
| :-: | :-: |
| Dwupunktowa | Granica + najbliższa wartość z drugiej strony |
| Trójpunktowa | Wartość poniżej + na granicy + powyżej (dokładniejsza) |


**4.3 Techniki białoskrzynkowe:**

| Technika | Cel |
| :-: | :-: |
| Testowanie instrukcji | Każda linia kodu wykonana ≥1 raz |
| Testowanie gałęzi | Każda gałąź IF/ELSE (TRUE i FALSE) wykonana ≥1 raz |


**5. Zarządzanie czynnościami testowymi.**

**5.1 Plan testów zawiera:**

| Element | Opis |
| :-: | :-: |
| Zakres i cele | Co i po co testujemy |
| Podejście | Poziomy, typy, techniki testowania |
| Zasoby | Ludzie, narzędzia, środowisko |
| Harmonogram | Kiedy co się dzieje |
| Ryzyka | Rejestr zidentyfikowanych ryzyk |
| Kryteria wejścia/wyjścia | Warunki rozpoczęcia/zakończenia |
| Sposób komunikacji | Jak raportujemy postęp |


**5.2 Kwadranty testowe:**

| **Kwadrant** | **Cel** | **Charakter** |
| :-: | :-: | :-: |
| Q1 | Technologiczny, wspiera zespół | Testy modułowe, integracyjne |
| Q2 | Biznesowy, wspiera zespół | Testy funkcjonalne, historyjek |
| Q3 | Biznesowy, krytyka produktu | Eksploracyjne, użyteczności, akceptacyjne |
| Q4 | Technologiczny, krytyka produktu | Wydajnościowe, inne niefunkcjonalne |


**5.3 Zarządzanie ryzykiem:**

| Pojęcie | Definicja |
| :-: | :-: |
| Ryzyko | Możliwe zdarzenie o negatywnym skutku |
| Poziom ryzyka | Prawdopodobieństwo × wpływ |
| Ryzyko projektowe | Zagraża realizacji projektu (opóźnienia, budżet, kadry) |
| Ryzyko produktowe | Zagraża jakości produktu (błędy, luki bezpieczeństwa) |
| Ryzyko rezydualne | Pozostałe po działaniach łagodzących |


**5.4 Raporty i metryki:**

| Pojęcie | Definicja |
| :-: | :-: |
| Raport o postępie testów | Regularny, na bieżąco |
| Sumaryczny raport z testów | Jeden, na koniec etapu/projektu |
| Metryki testowe | Liczba defektów, pokrycie, wykonane testy, ryzyko rezydualne |


**5.5 Severity vs Priority:**

| Pojęcie | Definicja |
| :-: | :-: |
| Severity | Jak poważny jest wpływ defektu na system |
| Priority | Jak szybko trzeba go naprawić |


**6. Narzędzia testowe.**

### **6.1 Kategorie narzędzi:**

| Kategoria | Przykłady |
| :-: | :-: |
| Zarządzania | Jira, TestRail, Xray |
| Testowania statycznego | SonarQube, ESLint, Pylint |
| Projektowania/implementacji testów | TestRail, Xray, Zephyr |
| Wykonywania testów | Selenium, Playwright, Cypress, Appium |
| Pomiaru pokrycia | JaCoCo (Java), coverage.py (Python), Istanbul/nyc (JS) |
| Testowania niefunkcjonalnego | Apache JMeter, Gatling, k6 |
| DevOps / CI/CD | Jenkins, GitHub Actions, GitLab CI/CD, Azure DevOps |
| Współpracy | Slack, Microsoft Teams, Confluence |
| Kodu i wersji | Git, GitHub, GitLab, Bitbucket |
| Konteneryzacji | Docker, Kubernetes |
| API | Postman, Insomnia, SoapUI |
| Automatyzacji mobilnej | Appium, Espresso, XCUITest |
| Raportowania wyników | Allure Report, TestRail, Zephyr |


