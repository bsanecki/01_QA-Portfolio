# SQL notes

## 0. Typy danych

| Typ | Znaczenie |
|---|---|
| `TEXT` | tekst |
| `INTEGER` | liczba całkowita |
| `REAL` / `FLOAT` | liczba z przecinkiem |
| `BOOLEAN` | TRUE / FALSE |
| `DATE` | data |
| `DATETIME` | data i czas |

---

## 1. Tworzenie tabeli

```sql
CREATE TABLE nazwa_tabeli ( nazwa_kolumny typ_danych, nazwa_kolumny typ_danych, ... );
```
tworzy nową tabelę

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```
klucz główny z automatycznie nadawanym numerem

---

## 2. Dodawanie danych

```sql
INSERT INTO nazwa_tabeli VALUES (..., ..., ...);
```
dodaje nowy rekord (wartości dla wszystkich kolumn, po kolei)

```sql
INSERT INTO nazwa_tabeli (kolumna1, kolumna2) VALUES (..., ...);
```
dodaje rekord, podając wartości tylko dla wybranych kolumn

---

## 3. Wyświetlanie danych

```sql
SELECT * FROM nazwa_tabeli;
```
wyświetla całą tabelę

```sql
SELECT nazwa_kolumny FROM nazwa_tabeli;
```
wyświetla wybraną kolumnę

```sql
SELECT * FROM nazwa_tabeli WHERE wartość > 2000 ORDER BY nazwa_kolumny;
```
wyświetla rekordy spełniające warunek i sortuje je rosnąco (malejąco → `ORDER BY nazwa_kolumny DESC`)

![sql_screen_1](screens/sql_screen_1.png)

---

## 4. Grupowanie

```sql
SELECT nazwa_kolumny, inna_nazwa_kolumny FROM nazwa_tabeli GROUP BY nazwa_kolumny;
```
grupuje wiersze po wartościach `nazwa_kolumny` — używa się głównie z funkcjami typu `SUM`, `COUNT` (kolejność wyniku ustawia się przez `ORDER BY`, malejąco → `DESC`)

![sql_screen_2](screens/sql_screen_2.png)

---

## 5. Funkcje agregujące

```sql
SELECT SUM(nazwa_kolumny) FROM nazwa_tabeli;
```
sumuje wszystkie wartości z danej kolumny

```sql
SELECT COUNT(nazwa_kolumny) FROM nazwa_tabeli;
```
liczy liczbę wierszy (rekordów)

```sql
SELECT AVG(nazwa_kolumny) FROM nazwa_tabeli;
```
liczy średnią wartość z danej kolumny

```sql
SELECT MIN(nazwa_kolumny) FROM nazwa_tabeli;
```
zwraca najmniejszą wartość z danej kolumny

```sql
SELECT MAX(nazwa_kolumny) FROM nazwa_tabeli;
```
zwraca największą wartość z danej kolumny

---

## 6. Operatory logiczne (AND, OR, IN)

```sql
SELECT title FROM songs WHERE mood = 'epic' OR released > 1990;
```
wyświetla wiersze spełniające **przynajmniej jeden** z warunków

```sql
SELECT title FROM songs WHERE mood = 'epic' AND released > 1990 AND duration < 240;
```
wyświetla wiersze spełniające **wszystkie** warunki naraz (można łączyć dowolną liczbę warunków przez `AND`)

```sql
SELECT title, artist FROM songs WHERE artist IN (SELECT name FROM artists WHERE genre = 'Pop');
```
`IN` sprawdza, czy wartość znajduje się na liście — lista może być podana ręcznie (`IN ('a', 'b')`) albo pochodzić z podzapytania (`SELECT ...`) jak wyżej

![sql_screen_3](screens/sql_screen_3.png)

---

## 7. HAVING

```sql
SELECT type, SUM(calories) AS total_calories FROM exercise_logs
    GROUP BY type
    HAVING total_calories > 150;
```
filtruje **wyniki po zgrupowaniu** (na wartościach z funkcji agregujących typu `SUM`, `AVG`) — `WHERE` tego nie potrafi, bo działa przed grupowaniem

```sql
SELECT type, AVG(calories) AS avg_calories FROM exercise_logs
    GROUP BY type
    HAVING avg_calories > 70;
```
to samo, tylko warunek na średniej zamiast sumy

```sql
SELECT type FROM exercise_logs GROUP BY type HAVING COUNT(*) >= 2;
```
`HAVING` można łączyć też z `COUNT` — tu: pokazuje tylko typy występujące co najmniej 2 razy

```sql
SELECT author, SUM(words) AS total_words FROM books GROUP BY author HAVING SUM(words) > 1000000;
```
w `HAVING` warunek można podać wprost na funkcji agregującej (`SUM(words) > ...`), nie tylko przez alias (`total_words > ...`) — działa tak samo

![sql_screen_4](screens/sql_screen_4.png)

---

## 8. ROUND

```sql
SELECT name, ROUND(fraction_completed * 100) AS percent_completed FROM student_grades;
```
zaokrągla wynik obliczenia do liczby całkowitej (przydatne np. przy liczeniu procentów)

---

## 9. CASE

```sql
SELECT name,
    CASE
        WHEN number_grade > 90 THEN 'A'
        WHEN number_grade > 80 THEN 'B'
        WHEN number_grade > 70 THEN 'C'
        ELSE 'F'
    END AS letter_grade
FROM student_grades;
```
`CASE` sprawdza warunki po kolei (`WHEN ... THEN ...`) i zwraca wartość przypisaną do pierwszego spełnionego — jeśli żaden nie pasuje, zwraca wartość z `ELSE`. Działa jak `if/else` wewnątrz `SELECT`, wynik można nazwać aliasem (`AS letter_grade`)

Można łączyć z `GROUP BY`, żeby policzyć, ile wierszy wpadło do każdej kategorii:
```sql
SELECT
    CASE
        WHEN number_grade > 90 THEN 'A'
        WHEN number_grade > 80 THEN 'B'
        WHEN number_grade > 70 THEN 'C'
        ELSE 'F'
    END AS letter_grade,
    COUNT(*) AS count
FROM student_grades
GROUP BY letter_grade;
```

![sql_screen_5](screens/sql_screen_5.png)

---

## 10. LIKE

```sql
SELECT * FROM nazwa_tabeli WHERE nazwa_kolumny LIKE 'wzorzec%';
```
wyszukuje wartości pasujące do wzorca tekstowego — `%` oznacza dowolną liczbę dowolnych znaków, `_` oznacza dokładnie jeden dowolny znak

np.
```sql
SELECT * FROM songs WHERE title LIKE 'A%';
```
zwraca tytuły zaczynające się na "A"

---

## 11. JOIN

```sql
SELECT * FROM student_grades;
```
zwykłe zapytanie z jednej tabeli — punkt wyjścia do porównania z poniższymi

**Cross join** — łączy każdy wiersz z jednej tabeli z każdym wierszem drugiej (wszystkie możliwe kombinacje):
```sql
SELECT * FROM student_grades, students;
```

**Implicit inner join** — cross join + warunek w `WHERE` łączący wiersze po wspólnej kolumnie:
```sql
SELECT * FROM student_grades, students
    WHERE student_grades.student_id = students.id;
```

**Explicit inner join (JOIN ... ON)** — czytelniejsza wersja tego samego, warunek łączenia w `ON` zamiast w `WHERE`:
```sql
SELECT students.first_name, students.last_name, students.email, student_grades.test, student_grades.grade
    FROM students
    JOIN student_grades
    ON students.id = student_grades.student_id
    WHERE grade > 90;
```
> `JOIN` (bez dopisku) domyślnie oznacza `INNER JOIN` — pokazuje tylko wiersze, dla których znaleziono dopasowanie w obu tabelach

**Outer join (LEFT OUTER JOIN)** — pokazuje wszystkie wiersze z lewej tabeli, nawet jeśli nie mają dopasowania w drugiej (wtedy puste kolumny = NULL):
```sql
SELECT students.first_name, students.last_name, student_projects.title
    FROM students
    LEFT OUTER JOIN student_projects
    ON students.id = student_projects.student_id;
```

**Self join** — tabela łączona sama ze sobą (przydatne, gdy jedna kolumna odwołuje się do innego wiersza tej samej tabeli, np. `buddy_id` wskazujący na innego ucznia). Trzeba nadać alias, żeby SQL rozróżnił "dwie kopie" tabeli:
```sql
SELECT id, first_name, last_name, buddy_id FROM students;

SELECT students.first_name, students.last_name, buddies.email AS buddy_email
    FROM students
    JOIN students buddies
    ON students.buddy_id = buddies.id;
```

**Kilka JOIN-ów naraz** — można łączyć więcej niż dwie tabele, dodając kolejne `JOIN ... ON` (tu z aliasami `a` i `b` dla dwóch różnych wierszy tej samej tabeli):
```sql
SELECT a.title, b.title FROM project_pairs
    JOIN student_projects a
    ON project_pairs.project1_id = a.id
    JOIN student_projects b
    ON project_pairs.project2_id = b.id;
```
---

## 12. SUBQUERY (podzapytania)

```sql
SELECT * FROM city
WHERE population > (
    SELECT AVG(population)
    FROM city
);
```
podzapytanie w nawiasie (`SELECT AVG(population) FROM city`) wykonuje się jako pierwsze i zwraca jedną wartość (tu: średnią populację), która jest potem używana w warunku `WHERE` zapytania głównego — zwraca miasta o populacji powyżej średniej

```sql
SELECT title, artist FROM songs
WHERE artist IN (
    SELECT name FROM artists WHERE genre = 'Pop'
);
```
podzapytanie może też zwracać listę wartości zamiast jednej — wtedy używa się go razem z `IN` (patrz też sekcja 6)

---

## 13. MOD — sprawdzanie parzystości

```sql
SELECT * FROM nazwa_tabeli WHERE MOD(id, 2) = 0;
```
`MOD(a, b)` zwraca resztę z dzielenia `a` przez `b` — tu: reszta z dzielenia `id` przez 2 równa 0, czyli wiersze o parzystym `id`

```sql
SELECT * FROM nazwa_tabeli WHERE MOD(id, 2) = 1;
```
to samo, ale dla wierszy o nieparzystym `id`

---

## 14. LENGTH

```sql
SELECT LENGTH(nazwa_kolumny) FROM nazwa_tabeli;
```
zwraca długość tekstu (liczbę znaków) w danej kolumnie

np.
```sql
SELECT city, LENGTH(city) FROM station;
```
zwraca nazwę miasta razem z liczbą znaków w tej nazwie
