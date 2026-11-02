# SQL Notes 

## 0. Data Types

| Type | Meaning |
|---|---|
| `TEXT` | text |
| `INTEGER` | whole number |
| `REAL` / `FLOAT` | decimal number |
| `BOOLEAN` | TRUE / FALSE |
| `DATE` | date |
| `DATETIME` | date and time |

---

## 1. Creating a Table

```sql
CREATE TABLE table_name ( column_name data_type, column_name data_type, ... );
```
creates a new table

```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```
primary key with an automatically assigned number

---

## 2. Adding Data

```sql
INSERT INTO table_name VALUES (..., ..., ...);
```
adds a new record (values for all columns, in order)

```sql
INSERT INTO table_name (column1, column2) VALUES (..., ...);
```
adds a record, providing values only for selected columns

---

## 3. Retrieving Data

```sql
SELECT * FROM table_name;
```
displays the entire table

```sql
SELECT column_name FROM table_name;
```
displays a selected column

```sql
SELECT * FROM table_name WHERE value > 2000 ORDER BY column_name;
```
displays records matching the condition and sorts them in ascending order (descending → `ORDER BY column_name DESC`)

![sql_screen_1](screens/sql_screen_1.png)

---

## 4. Grouping

```sql
SELECT column_name, other_column_name FROM table_name GROUP BY column_name;
```
groups rows by the values of `column_name` — mainly used together with functions such as `SUM`, `COUNT` (the order of the result is set with `ORDER BY`; descending → `DESC`)

![sql_screen_2](screens/sql_screen_2.png)

---

## 5. Aggregate Functions

```sql
SELECT SUM(column_name) FROM table_name;
```
sums all values in the given column

```sql
SELECT COUNT(column_name) FROM table_name;
```
counts the number of rows (records)

```sql
SELECT AVG(column_name) FROM table_name;
```
calculates the average value of the given column

```sql
SELECT MIN(column_name) FROM table_name;
```
returns the smallest value in the given column

```sql
SELECT MAX(column_name) FROM table_name;
```
returns the largest value in the given column

---

## 6. Logical Operators (AND, OR, IN)

```sql
SELECT title FROM songs WHERE mood = 'epic' OR released > 1990;
```
returns rows matching **at least one** of the conditions

```sql
SELECT title FROM songs WHERE mood = 'epic' AND released > 1990 AND duration < 240;
```
returns rows matching **all** of the conditions at once (any number of conditions can be chained with `AND`)

```sql
SELECT title, artist FROM songs WHERE artist IN (SELECT name FROM artists WHERE genre = 'Pop');
```
`IN` checks whether a value is present in a list — the list can be given manually (`IN ('a', 'b')`) or come from a subquery (`SELECT ...`) as shown above

![sql_screen_3](screens/sql_screen_3.png)

---

## 7. HAVING

```sql
SELECT type, SUM(calories) AS total_calories FROM exercise_logs
    GROUP BY type
    HAVING total_calories > 150;
```
filters **results after grouping** (on values produced by aggregate functions such as `SUM`, `AVG`) — `WHERE` cannot do this, since it runs before grouping

```sql
SELECT type, AVG(calories) AS avg_calories FROM exercise_logs
    GROUP BY type
    HAVING avg_calories > 70;
```
the same idea, but the condition is on the average instead of the sum

```sql
SELECT type FROM exercise_logs GROUP BY type HAVING COUNT(*) >= 2;
```
`HAVING` can also be combined with `COUNT` — here: shows only types that occur at least 2 times

```sql
SELECT author, SUM(words) AS total_words FROM books GROUP BY author HAVING SUM(words) > 1000000;
```
in `HAVING`, the condition can be written directly on the aggregate function (`SUM(words) > ...`), not only through an alias (`total_words > ...`) — both work the same way

![sql_screen_4](screens/sql_screen_4.png)

---

## 8. ROUND

```sql
SELECT name, ROUND(fraction_completed * 100) AS percent_completed FROM student_grades;
```
rounds the result of a calculation to a whole number (useful e.g. when calculating percentages)

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
`CASE` checks conditions in order (`WHEN ... THEN ...`) and returns the value assigned to the first one that matches — if none match, it returns the value from `ELSE`. It works like an `if/else` inside `SELECT`; the result can be given an alias (`AS letter_grade`)

It can be combined with `GROUP BY` to count how many rows fall into each category:
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
SELECT * FROM table_name WHERE column_name LIKE 'pattern%';
```
searches for values matching a text pattern — `%` matches any number of any characters, `_` matches exactly one character

e.g.
```sql
SELECT * FROM songs WHERE title LIKE 'A%';
```
returns titles starting with "A"

---

## 11. JOIN

```sql
SELECT * FROM student_grades;
```
a plain query on a single table — the starting point for comparison with the queries below

**Cross join** — combines every row from one table with every row from the other (all possible combinations):
```sql
SELECT * FROM student_grades, students;
```

**Implicit inner join** — a cross join plus a `WHERE` condition that matches rows on a shared column:
```sql
SELECT * FROM student_grades, students
    WHERE student_grades.student_id = students.id;
```

**Explicit inner join (JOIN ... ON)** — a more readable version of the same thing, with the matching condition in `ON` instead of `WHERE`:
```sql
SELECT students.first_name, students.last_name, students.email, student_grades.test, student_grades.grade
    FROM students
    JOIN student_grades
    ON students.id = student_grades.student_id
    WHERE grade > 90;
```
> `JOIN` on its own defaults to `INNER JOIN` — it only returns rows that have a match in both tables

**Outer join (LEFT OUTER JOIN)** — returns all rows from the left table, even if they have no match in the other table (in that case the extra columns are NULL):
```sql
SELECT students.first_name, students.last_name, student_projects.title
    FROM students
    LEFT OUTER JOIN student_projects
    ON students.id = student_projects.student_id;
```

**Self join** — a table joined with itself (useful when one column refers to another row of the same table, e.g. `buddy_id` pointing to another student). An alias is required so SQL can tell the "two copies" of the table apart:
```sql
SELECT id, first_name, last_name, buddy_id FROM students;

SELECT students.first_name, students.last_name, buddies.email AS buddy_email
    FROM students
    JOIN students buddies
    ON students.buddy_id = buddies.id;
```

**Multiple JOINs at once** — more than two tables can be combined by chaining additional `JOIN ... ON` clauses (here with aliases `a` and `b` for two different rows of the same table):
```sql
SELECT a.title, b.title FROM project_pairs
    JOIN student_projects a
    ON project_pairs.project1_id = a.id
    JOIN student_projects b
    ON project_pairs.project2_id = b.id;
```
---

## 12. SUBQUERY

```sql
SELECT * FROM city
WHERE population > (
    SELECT AVG(population)
    FROM city
);
```
the subquery in parentheses (`SELECT AVG(population) FROM city`) runs first and returns a single value (here: the average population), which is then used in the `WHERE` condition of the outer query — this returns cities with an above-average population

```sql
SELECT title, artist FROM songs
WHERE artist IN (
    SELECT name FROM artists WHERE genre = 'Pop'
);
```
a subquery can also return a list of values instead of a single one — in that case it's used together with `IN` (see also section 6)

---

## 13. MOD — Checking Even/Odd Numbers

```sql
SELECT * FROM table_name WHERE MOD(id, 2) = 0;
```
`MOD(a, b)` returns the remainder of dividing `a` by `b` — here: the remainder of `id` divided by 2 equals 0, i.e. rows with an even `id`

```sql
SELECT * FROM table_name WHERE MOD(id, 2) = 1;
```
the same idea, but for rows with an odd `id`

---

## 14. LENGTH

```sql
SELECT LENGTH(column_name) FROM table_name;
```
returns the length of a text value (number of characters) in the given column

e.g.
```sql
SELECT city, LENGTH(city) FROM station;
```
returns the city name together with the number of characters in that name
