# Git -  notatki dla QA testera (podstawy)

## 1. Start projektu

```bash
git init
```
Tworzy nowe, puste repozytorium Git w bieżącym folderze. Używasz tego, gdy zaczynasz nowy projekt od zera (np. własne portfolio testerskie).

```bash
git clone https://github.com/user/repo.git
```
Kopiuje istniejące repozytorium z GitHuba (albo innego serwera) na Twój komputer razem z całą historią zmian. To najczęstsza operacja na start — dołączasz do istniejącego projektu.

---

## 2. Sprawdzanie stanu repozytorium

```bash
git status
```
Pokazuje, co się aktualnie dzieje: które pliki zostały zmienione, które są gotowe do commita (staged), a które jeszcze nie są śledzone przez Git. To polecenie, którego używa się **najczęściej ze wszystkich** — zawsze warto sprawdzić `status` przed kolejnym krokiem.

```bash
git log
```
Pokazuje historię commitów — kto, kiedy i co zmienił (wraz z opisem commita). Przydatne, żeby sprawdzić, co działo się w projekcie wcześniej, np. kiedy pojawił się dany błąd.

```bash
git diff
```
Pokazuje dokładnie, **co się zmieniło** w plikach względem ostatniego commita — linia po linii (co dodano, co usunięto). Bardzo przydatne przy code review albo sprawdzaniu własnych zmian przed commitem.

---

## 3. Zapisywanie zmian

```bash
git add nazwa_pliku.txt
```
Dodaje plik do tzw. **staging area** — czyli oznacza go jako gotowy do zapisania w następnym commicie. Możesz też dodać wszystko naraz:
```bash
git add .
```

```bash
git commit -m "Opis zmian"
```
Zapisuje wszystkie dodane (staged) zmiany jako nowy punkt w historii projektu, z opisem tego, co zostało zrobione.

**Typowy przepływ:**
```bash
git add .
git commit -m "Add login test cases"
```

---

## 4. Praca z repozytorium zdalnym (remote)

```bash
git push
```
Wysyła Twoje lokalne commity na serwer (np. GitHub), żeby inni też mogli je zobaczyć.

```bash
git pull
```
Pobiera najnowsze zmiany z serwera **i od razu je łączy** z Twoją lokalną gałęzią. To skrót od `git fetch` + `git merge`.

```bash
git fetch
```
Pobiera najnowsze zmiany z serwera, ale **nie łączy** ich automatycznie z Twoją pracą — możesz najpierw zobaczyć, co się zmieniło, zanim zdecydujesz się to wciągnąć do swojego kodu.

> **Różnica `pull` vs `fetch`:** `pull` = pobierz i od razu zastosuj. `fetch` = tylko pobierz i pozwól Ci zdecydować.

---

## 5. Praca z gałęziami (branches)

```bash
git branch
```
Pokazuje listę wszystkich gałęzi w repozytorium i zaznacza, na której aktualnie jesteś.

```bash
git branch nazwa-galezi
```
Tworzy nową gałąź (ale nie przełącza się na nią).

```bash
git switch nazwa-galezi
```
Przełącza Cię na wskazaną gałąź. Możesz też od razu stworzyć i przełączyć się na nową gałąź jedną komendą:
```bash
git switch -c nowa-galaz
```

```bash
git merge nazwa-galezi
```
Łączy wskazaną gałąź z tą, na której aktualnie jesteś — np. dołączasz swoje zmiany z gałęzi `feature/login-tests` do `main`.

**Typowy przepływ pracy na gałęziach:**
```bash
git switch -c feature/new-test-cases
# ... praca nad zmianami ...
git add .
git commit -m "Add new test cases for checkout"
git switch main
git merge feature/new-test-cases
```

---

## 6. Cofanie zmian

```bash
git restore nazwa_pliku.txt
```
Cofa niezapisane (niescommitowane) zmiany w pliku do stanu z ostatniego commita — czyli "anuluj to, co właśnie zmieniłem w tym pliku".

```bash
git reset
```
Cofa zmiany dodane przez `git add` (czyli wyjmuje pliki ze staging area), ale **nie usuwa** samych zmian w plikach — nadal tam są, tylko nie są już oznaczone do commita.

> **Różnica:** `restore` cofa zmiany w treści pliku. `reset` cofa to, co zostało dodane do `git add`, ale nie rusza zawartości plików.

---

## 7. Stash — tymczasowe odłożenie zmian

```bash
git stash
```
Tymczasowo "chowa" Twoje niescommitowane zmiany (jakby schował je do szuflady), żebyś mógł np. przełączyć się na inną gałąź bez commitowania niedokończonej pracy.

```bash
git stash pop
```
Przywraca ostatnio schowane zmiany z powrotem do Twojego katalogu roboczego.

**Typowy scenariusz:** pracujesz nad czymś, ale musisz pilnie przełączyć się na inną gałąź, żeby coś sprawdzić:
```bash
git stash
git switch main
# ... sprawdzasz coś na main ...
git switch feature/moja-galaz
git stash pop
```

---

## 8. Pozostałe przydatne polecenia

```bash
git remote -v
```
Pokazuje, z jakim repozytorium zdalnym (np. GitHub) jest powiązane Twoje lokalne repozytorium — przydatne, żeby sprawdzić, gdzie faktycznie trafi `git push`.

```bash
git log --oneline
```
Skrócona wersja `git log` — jeden commit = jedna linijka. Dużo wygodniejsze do szybkiego przeglądu historii niż pełny `git log`.

---

## 9. Plik .gitignore

`.gitignore` to nie jest komenda, tylko plik w repozytorium, w którym wypisuje się, jakich plików/folderów Git ma **nie śledzić** (np. plików tymczasowych, danych logowania, folderów typu `node_modules`). Bardzo często potrzebne w praktyce, żeby przypadkiem nie wrzucić do repo czegoś, czego nie powinno tam być.

Przykładowa zawartość pliku `.gitignore`:
```
node_modules/
.env
*.log
```

---

## 10. Dobra praktyka opisów commitów

Opis commita powinien być krótki, konkretny i napisany w trybie rozkazującym, opisujący co dana zmiana robi, a nie co zostało zrobione. Przykładowo:

```
Add test cases for password reset
Fix broken login test
Update README with setup instructions
```

Ogólnikowych opisów, takich jak `"zmiany"` czy `"fix"`, należy unikać, ponieważ nie dostarczają żadnej użytecznej informacji o faktycznej zawartości commita — ani dla innych osób przeglądających historię projektu, ani dla samego autora w późniejszym czasie.
