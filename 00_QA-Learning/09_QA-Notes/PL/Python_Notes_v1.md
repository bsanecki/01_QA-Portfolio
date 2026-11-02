# Python - notatki

## 1. Typy danych

| Typ | Opis | Przykład |
|---|---|---|
| `int` | liczby całkowite (ujemne, 0, dodatnie) | `5`, `-3`, `1000` |
| `float` | liczby zmiennoprzecinkowe | `3.14`, `-0.5`, `2.0` |
| `str` | tekst | `"hello"`, `'Python'` |
| `bool` | wartość logiczna (`True`=1, `False`=0) | `True`, `False` |
| `list` | lista | `[1, 2, 3]` |
| `tuple` | krotka (niemodyfikowalna) | `(1, 2)` |
| `dict` | słownik (klucz: wartość) | `{"name": "Ala"}` |
| `set` | zbiór (bez duplikatów) | `{1, 2, 3}` |

```python
print(type(dana))          # sprawdzenie typu danej
b = 4
k = int(b)                 # konwersja na inny typ (int, float, str, bool...)
```

### Wartości bool

```python
print(3 > 15)   # False
print(3 < 15)   # True
```

---

## 2. Wejście / wyjście

```python
zmienna = input()          # użytkownik wpisuje wartość
print(zmienna)
```

### `print()` — warianty

```python
print("Hello\nworld")                  # Hello / world (nowa linia)
print("Hello", "world", sep="..")      # Hello..world
print("My name is", end="")            # bez znaku końca linii
print("Marek")                         # -> My name is Marek
```

---

## 3. Operatory

| Operator | Znaczenie | Przykład | Wynik |
|---|---|---|---|
| `**` | potęgowanie | `2 ** 3` | `8` |
| `*` | mnożenie | `2 * 3` | `6` |
| `/` | dzielenie | `6 / 2` | `3.0` |
| `//` | dzielenie całkowite | `7 // 2` | `3` |
| `%` | reszta z dzielenia | `7 % 2` | `1` |
| `+` | dodawanie | `2 + 2` | `4` |
| `-` | odejmowanie | `5 - 3` | `2` |

Łączenie stringów: `wyraz = "Foot" + "ball"` → `"Football"`

| Rodzaj | Operatory | Przykład |
|---|---|---|
| Arytmetyczne | `+ - * / % ** //` | `5 + 3 = 8` |
| Przypisania | `= += -= *= /=` | `x += 2` → `x = x + 2` |
| Porównania | `== != > < >= <=` | `5 > 3` → `True` |
| Logiczne | `and or not` | `(x > 0) and (x < 10)` |
| Bitowe | `& \| ^ ~ << >>` | operacje na bitach liczb całkowitych |
| Tożsamości | `is`, `is not` | czy dwie zmienne wskazują ten sam obiekt |
| Przynależności | `in`, `not in` | czy element należy do kolekcji |

---

## 4. Instrukcje warunkowe

```python
age = 18
if age == 18:
    print("Ma 18 lat")
elif age > 18:
    print("Ma więcej niż 18 lat")
else:
    print("Jest nieletni")
```

---

## 5. Pętle

### `while` — dopóki warunek jest `True`

```python
number = int(input())
while number <= 5:
    print(number)
    number = number - 1
```

### `for` — dla każdego elementu sekwencji

```python
for i in range(4):
    print("Hello")
# Hello x4
```

---

## 6. Listy

Indeksowanie — dodatnie od lewej (od 0), ujemne od prawej (od -1):

```
indeks:  0  1  2  3  4  5  6  7  8  9  10 11
L    =   M  o  n  t  y     P  y  t  h  o  n
indeks: -12-11-10 -9 -8 -7 -6 -5 -4 -3 -2 -1
```

```python
my_list = [1, None, True, "text", 256, 0]

my_list[1] = "?"            # aktualizacja wartości pod indeksem
print(my_list[3])           # "text"
print(my_list[-1])          # 0 (indeksowanie od końca)

my_list.insert(0, "first")  # dodaje na początek
my_list.append("last")      # dodaje na koniec

del my_list[2]               # usuwa 3. element
del my_list                  # usuwa całą listę

len(my_list)                 # liczba elementów

list2 = list1                # obie zmienne wskazują tę samą listę
```

### Slicing

```python
sample = ["A", "B", "C", "D", "E"]

sample[2:-1]     # ['C', 'D']
my_list[2:]      # od 3. elementu do końca
my_list[:2]      # pierwsze dwa
my_list[-2:]     # dwa ostatnie

del my_list[0:2] # usuwa pierwsze dwa
del my_list[:]   # czyści całą listę
```

### Metody list

```python
my_list.reverse()   # odwraca kolejność elementów
my_list.sort()       # sortuje listę
my_list.count(x)     # liczba wystąpień x
my_list.index(x)     # indeks pierwszego wystąpienia x
```

### Listy zagnieżdżone

```python
lista = [1, "a", [2, "b", [3, "c"]]]
print(lista[2][2][1])   # dostęp do "c"

# tylko elementy spoza zagnieżdżonych list
for x in lista:
    if not isinstance(x, list):
        print(x)
```

---

## 7. Krotki

Niemodyfikowalne po utworzeniu.

```python
krotka = (1, 2, 3)
print(krotka[0])   # 1
```

---

## 8. Słowniki

```python
slownik = {1: 'a', 2: 'b', 3: 'c'}

slownik[1]              # 'a'
slownik[4] = 30          # dodaje nowy klucz i wartość
del slownik[4]           # usuwa klucz

slownik.keys()           # wszystkie klucze
slownik.values()          # wszystkie wartości
slownik.items()           # pary (klucz, wartość)

# tworzenie słownika z dwóch list
a = [1, 2, 3]
b = ['a', 'b', 'c']
slownik = dict(zip(a, b))   # {1: 'a', 2: 'b', 3: 'c'}
```

---

## 9. Zbiory (set)

```python
zbior = {'a', 'b', 'c'}
set("abcd")          # tworzy zbiór z ciągu znaków, kolejność przypadkowa
zbior = set()          # pusty zbiór

a = {'a', 'b', 'c'}
b = {'c', 'd', 'e'}

a.union(b)                 # a | b     -> a b c d e
a.difference(b)             # a - b     -> to, co ma a, a nie ma b
a.intersection(b)           # a & b     -> część wspólna
a.symmetric_difference(b)   # a ^ b     -> to, czego NIE mają wspólnego
a.issubset(b)                # czy wszystkie elementy a są w b
a.add('w')                   # dodaje element do zbioru
```

---

## 10. Działania bitowe

Działają na poziomie bitów liczb całkowitych (`int`).

| Operator | Nazwa | Opis | Przykład |
|---|---|---|---|
| `&` | AND | bity 1 w obu | `5 & 3` → `1` |
| `\|` | OR | bity 1 w jednym lub obu | `5 \| 3` → `7` |
| `^` | XOR | bity 1 w jednym, ale nie obu | `5 ^ 3` → `6` |
| `~` | NOT | odwraca wszystkie bity | `~5` → `-6` |
| `<<` | przesunięcie w lewo | mnoży przez 2ⁿ | `2 << 2` → `8` |
| `>>` | przesunięcie w prawo | dzieli przez 2ⁿ (zaokr. w dół) | `8 >> 1` → `4` |

---

## 11. Funkcje

```python
def nazwa_funkcji():
    # ciało funkcji
    pass

x = 1

def liczyc():
    global x        # dostęp do zmiennej globalnej
    return x + 1

liczyc()      # 2

locals()      # wszystkie zmienne w danym środowisku (np. wewnątrz funkcji)
```

---

## 12. Wyjątki

```python
x = '10'   # string, nie liczba

try:
    x == 5
    print("X jest równe 5!")
except:
    print("X nie jest równe 5")
finally:
    print("Zawsze będę")   # wykona się zawsze, niezależnie od błędu
```

### Wbudowane wyjątki

| Wyjątek | Opis |
|---|---|
| `BaseException` | najbardziej ogólny wyjątek, po nim dziedziczą wszystkie inne |
| `ArithmeticError` | błędy arytmetyczne, np. dzielenie przez zero |
| `AssertionError` | rzucany przez `assert`, gdy warunek jest fałszywy |
| `IndexError` | odwołanie do nieistniejącego indeksu w sekwencji |
| `KeyError` | odwołanie do nieistniejącego klucza w słowniku |
| `ImportError` | import modułu się nie powiódł |
| `KeyboardInterrupt` | przerwanie programu przez użytkownika (Ctrl-C) |
| `LookupError` | abstrakcyjny wyjątek związany z błędnymi odwołaniami w kolekcjach |
| `MemoryError` | brak pamięci do wykonania operacji |
| `OverflowError` | wynik operacji arytmetycznej zbyt duży do przechowania |

### Własny wyjątek

```python
class FileEmptyError(Exception):
    pass
```

---

## 13. Moduły

| Termin | Opis |
|---|---|
| Moduł | plik `.py` z kodem (funkcje, klasy, zmienne) |
| Pakiet | folder z modułami i plikiem `__init__.py` |
| `__name__` | określa, czy plik jest uruchamiany czy importowany |
| `sys.path` | lista ścieżek, gdzie Python szuka modułów |
| `__init__.py` | plik inicjalizujący pakiet |
| Import z ZIP | możliwość importowania modułów z archiwów `.zip` |

```python
import math                        # importuje cały moduł
from math import sin               # importuje tylko funkcję sin
from math import *                  # importuje wszystko z modułu
import math as nazwa                # import pod inną nazwą
from math import sin as s, pi as PI # import z aliasami
```

### Własny moduł

```python
# plik nazwa.py zawiera kod funkcji

import nazwa
nazwa()   # wywołanie funkcji z modułu
```

### Specjalna zmienna `__name__`

```python
__name__ == "__main__"        # gdy plik uruchamiany bezpośrednio
__name__ == "nazwa_modulu"    # gdy plik zaimportowany jako moduł
```

Pozwala testować moduł, gdy jest uruchamiany samodzielnie.

### Ukrywanie elementów

Przedrostek `_` lub `__` przed nazwą zmiennej/funkcji oznacza konwencję "prywatności" — nie chroni fizycznie przed dostępem, tylko sygnalizuje intencję.

### Ścieżki modułów (`sys.path`)

```python
import sys
sys.path.append('ścieżka/do/folderu')   # dodanie własnego folderu do wyszukiwania modułów
```

### Struktura pakietu

```
packages/
└── extra/
    ├── __init__.py
    ├── iota.py
    └── good/
        ├── __init__.py
        ├── alpha.py
        └── best/
            ├── __init__.py
            └── sigma.py
```

```python
from extra.good.best import sigma
import extra.iota
```

### Podstawowe polecenia `pip`

| Polecenie | Co robi |
|---|---|
| `pip --version` | pokazuje wersję pip |
| `pip list` | wyświetla listę zainstalowanych pakietów |
| `pip show <pakiet>` | pokazuje szczegóły i zależności danego pakietu |
| `pip search <ciąg>` | szuka pakietów na PyPI zawierających ciąg |
| `pip install <nazwa>` | instaluje pakiet globalnie |
| `pip install --user <nazwa>` | instaluje pakiet lokalnie dla użytkownika |
| `pip install -U <nazwa>` | aktualizuje pakiet |
| `pip uninstall <nazwa>` | usuwa pakiet |

---

## 14. Znaki i kodowanie

```python
ord(char)    # znak -> kod liczbowy
chr(code)    # kod liczbowy -> znak
```

- **ASCII** — podstawowy zestaw 128 znaków (kody 0–127); `ord('A') = 65`, `ord('a') = 97` (różnica 32).
- **Unicode** — globalny standard kodowania (>1 mln znaków), pierwsze 128 to ASCII. Python 3 używa Unicode dla wszystkich `str`.
- **UTF-8** — domyślne kodowanie w Pythonie 3, zmienna długość (ASCII = 1 bajt, inne znaki = 2–4 bajty), kompatybilne z ASCII.
- **Code pages** — starsze kodowania zależne od języka, niejednoznaczne — unikać.
- **UCS-4** — 4 bajty na znak, mało efektywne, rzadko używane.

```python
miasto = "Łódź"
print(ord('Ł'))   # 321
print(chr(321))   # 'Ł'

with open('plik.txt', encoding='utf-8') as f:
    dane = f.read()
```

### Tabela ASCII (0–127)

| Znak | Kod | Znak | Kod | Znak | Kod | Znak | Kod |
|---|---|---|---|---|---|---|---|
| NUL | 0 | spacja | 32 | @ | 64 | ` | 96 |
| SOH | 1 | ! | 33 | A | 65 | a | 97 |
| STX | 2 | " | 34 | B | 66 | b | 98 |
| ETX | 3 | # | 35 | C | 67 | c | 99 |
| EOT | 4 | $ | 36 | D | 68 | d | 100 |
| ENQ | 5 | % | 37 | E | 69 | e | 101 |
| ACK | 6 | & | 38 | F | 70 | f | 102 |
| BEL | 7 | ' | 39 | G | 71 | g | 103 |
| BS | 8 | ( | 40 | H | 72 | h | 104 |
| HT | 9 | ) | 41 | I | 73 | i | 105 |
| LF | 10 | * | 42 | J | 74 | j | 106 |
| VT | 11 | + | 43 | K | 75 | k | 107 |
| FF | 12 | , | 44 | L | 76 | l | 108 |
| CR | 13 | - | 45 | M | 77 | m | 109 |
| SO | 14 | . | 46 | N | 78 | n | 110 |
| SI | 15 | / | 47 | O | 79 | o | 111 |
| DLE | 16 | 0 | 48 | P | 80 | p | 112 |
| DC1 | 17 | 1 | 49 | Q | 81 | q | 113 |
| DC2 | 18 | 2 | 50 | R | 82 | r | 114 |
| DC3 | 19 | 3 | 51 | S | 83 | s | 115 |
| DC4 | 20 | 4 | 52 | T | 84 | t | 116 |
| NAK | 21 | 5 | 53 | U | 85 | u | 117 |
| SYN | 22 | 6 | 54 | V | 86 | v | 118 |
| ETB | 23 | 7 | 55 | W | 87 | w | 119 |
| CAN | 24 | 8 | 56 | X | 88 | x | 120 |
| EM | 25 | 9 | 57 | Y | 89 | y | 121 |
| SUB | 26 | : | 58 | Z | 90 | z | 122 |
| ESC | 27 | ; | 59 | [ | 91 | { | 123 |
| FS | 28 | < | 60 | \\ | 92 | \| | 124 |
| GS | 29 | = | 61 | ] | 93 | } | 125 |
| RS | 30 | > | 62 | ^ | 94 | ~ | 126 |
| US | 31 | ? | 63 | _ | 95 | DEL | 127 |

---

## 15. Klasy (OOP)

### Definicja klasy

```python
class NazwaKlasy():
    # kod globalny dla klasy

    def __init__(self, cos, cos2):   # konstruktor
        self.cos = cos
        self.cos2 = cos2

    def funkcja(self):
        pass

    def __repr__(self):
        return "Nazwa klasy"

    def __str__(self):
        return "opis obiektu"

NazwaKlasy.__dict__   # wszystkie atrybuty klasy
```

### Klasa i obiekt

- **Klasa** — szablon obiektu: atrybuty i metody.
- **Obiekt** — konkretna instancja klasy, należy do swojej klasy i wszystkich jej superklas.
- `self` — odnosi się do konkretnego obiektu, pierwszy parametr każdej metody.

```python
class TheSimplestClass:
    pass

my_first_object = TheSimplestClass()
```

### Dziedziczenie

- Klasa może mieć **podklasy**, które dziedziczą po **superklasie**.
- Klasa potomna może nadpisywać metody klasy bazowej (**override**).
- Konstruktor klasy bazowej wywołujemy ręcznie przez `super().__init__()`.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print("Animal speaks")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        super().speak()
        print("Woof!")
```

### Zmienne instancji i klasowe

```python
class Example:
    counter = 0            # zmienna klasowa — współdzielona przez wszystkie obiekty

    def __init__(self):
        Example.counter += 1
        self.instance_var = 123   # zmienna instancji — unikalna dla obiektu
```

Prywatność zmiennej: przedrostek `__` (name mangling), np. `self.__stack_list`.

### Proceduralne vs obiektowe (przykład: stos)

```python
# Proceduralnie
stack = []

def push(val):
    stack.append(val)

def pop():
    val = stack[-1]
    del stack[-1]
    return val
# Wada: globalna lista, brak enkapsulacji, tylko jeden stos naraz

# Obiektowo
class Stack:
    def __init__(self):
        self.__stack_list = []

    def push(self, val):
        self.__stack_list.append(val)

    def pop(self):
        val = self.__stack_list[-1]
        del self.__stack_list[-1]
        return val
# Zaleta: enkapsulacja, wiele niezależnych stosów, łatwe rozszerzanie
```

### Sprawdzanie typów i dziedziczenia

```python
isinstance(obj, Klasa)                 # czy obj jest instancją Klasa lub jej podklasy
issubclass(KlasaPotomna, KlasaBazowa)  # czy klasa dziedziczy po innej
type(obj)                               # zwraca klasę obiektu
```

Wielodziedziczenie jest możliwe, ale wymaga uwagi (MRO — Method Resolution Order).

---

## 16. Generatory, iteratory, lambda, closures

### Iterator

Obiekt implementujący:
- `__iter__()` — zwraca iterator (zwykle `self`)
- `__next__()` — zwraca kolejny element lub rzuca `StopIteration`

`range()` to wbudowany generator.

### `yield`

Działa jak `return`, ale pauzuje funkcję i pozwala ją wznowić — zwraca generator.

```python
def fun(n):
    for i in range(n):
        yield i

def powers_of_2(n):
    power = 1
    for i in range(n):
        yield power
        power *= 2

list(fun(5))   # konwersja generatora na listę
```

### List comprehension vs generator expression

```python
[x for x in range(5)]    # zwraca listę
(x for x in range(5))     # zwraca generator (nie ma len())
```

### Lambda

```python
sqr = lambda x: x * x
print(sqr(4))   # 16

def print_function(args, fun):
    for x in args:
        print(fun(x))

print_function(range(5), lambda x: x**2)
```

### `map()` i `filter()`

```python
list(map(lambda x: x * 2, [1, 2, 3]))     # [2, 4, 6]
list(filter(lambda x: x > 0, [-2, 0, 3]))  # [3]
```

### Closures (domknięcia)

Funkcja pamiętająca zmienne z zakresu zewnętrznego, nawet po zakończeniu działania funkcji zewnętrznej.

```python
def outer(x):
    def inner(y):
        return x + y
    return inner

add_5 = outer(5)
print(add_5(3))   # 8
```

---

## 17. Pliki i strumienie

```python
stream = open(filename, mode, encoding='utf-8')
stream.close()
```

### Ścieżki

- Windows: `C:\\folder\\plik.txt` lub `C:/folder/plik.txt`
- Linux/Unix: `/home/user/plik.txt` (case-sensitive)

### Tryby otwarcia

| Tryb | Znaczenie |
|---|---|
| `r` | odczyt |
| `w` | zapis (nadpisuje plik) |
| `a` | dopisywanie na końcu |
| `r+` | odczyt i zapis, plik musi istnieć |
| `w+` | zapis i odczyt, tworzy nowy lub czyści |
| `x` | tworzy nowy plik, błąd jeśli istnieje |
| `+b` | dodane do trybu → tryb binarny, np. `rb` |
| `t` | tryb tekstowy (domyślny) |

### Predefiniowane strumienie

```python
sys.stdin    # wejście standardowe (używane przez input())
sys.stdout   # wyjście standardowe (używane przez print())
sys.stderr   # wyjście błędów
```

### Obsługa błędów IO

```python
errno.ENOENT   # plik nie istnieje
errno.EACCES   # brak dostępu
os.strerror(errno_code)   # opis błędu
```

### Odczyt pliku tekstowego

```python
stream.read(n)        # odczytuje n znaków
stream.read()          # odczytuje cały plik
stream.readline()      # odczytuje jedną linię
stream.readlines()     # zwraca listę linii

for line in open("file.txt", "rt"):
    print(line, end='')
```

### Zapis do pliku tekstowego

```python
# otwarcie w trybie 'w' (nadpisz) lub 'a' (dopisz)
stream.write("tekst\n")   # nie dodaje \n automatycznie
```

### Dane binarne

```python
data = bytearray(range(10, 20))
with open("binary.bin", "wb") as f:
    f.write(data)

data = bytearray(10)
with open("binary.bin", "rb") as f:
    f.readinto(data)

# lub
with open("binary.bin", "rb") as f:
    data = bytearray(f.read())
```

### Podsumowanie metod

```python
read(n)            # n znaków
read()              # cały plik
readline()          # jedna linia
readlines()         # lista linii
readinto(bytearray) # dane binarne
write(string)        # zapis tekstu
write(bytearray)     # zapis binarny
```

---

## 18. Moduł `os`

```python
import os

os.uname()      # (Unix) tuple: sysname, nodename, release, version, machine
platform.uname()  # odpowiednik dla Windows

os.name          # 'posix' (Unix/Linux/Mac), 'nt' (Windows), 'java' (Jython)

os.mkdir(path)         # tworzy pojedynczy katalog (błąd jeśli istnieje)
os.makedirs(path)       # rekurencyjnie tworzy całą ścieżkę katalogów
os.listdir([path])      # lista plików/katalogów

os.chdir(path)          # zmienia bieżący katalog roboczy
os.getcwd()             # zwraca ścieżkę bieżącego katalogu

os.rmdir(path)          # usuwa pusty katalog
os.removedirs(path)     # usuwa katalog i puste katalogi nadrzędne

os.system(cmd)          # wykonuje polecenie systemowe
```

---

## 19. Moduł `time`

```python
import time

print("Start")
time.sleep(2)     # pauza 2 sekundy
print("Koniec")

time.time()             # aktualny timestamp (float)
time.ctime([timestamp]) # czytelna data jako string
time.gmtime()             # struct_time (UTC)
time.localtime()          # struct_time (czas lokalny)
time.asctime(struct_time) # czytelny string daty
time.mktime(struct_time)  # timestamp
time.strftime(fmt[, t])   # string z datą/czasem
time.strptime(str, fmt)   # parsuje string na struct_time
```

`struct_time` — atrybuty: `tm_year`, `tm_mon`, `tm_mday`, `tm_hour` ... `tm_isdst`, dostępne też jako krotka po indeksach 0–8.

---

## 20. Wybrane moduły

### `dir()` — zawartość modułu

```python
import math
print(dir(math))   # wszystkie funkcje i zmienne modułu (działa po import nazwa_modulu)
```

### `math`

```python
import math

# trygonometria (radiany)
math.sin(x); math.cos(x); math.tan(x)
math.asin(x); math.acos(x); math.atan(x)

math.pi                # stała π
math.radians(180)       # stopnie -> radiany
math.degrees(x)         # radiany -> stopnie

math.e                  # stała Eulera
math.exp(x)              # e^x
math.log(x)               # ln(x)
math.log(x, b)             # log o podstawie b
math.log10(x); math.log2(x)

pow(2, 3)               # 2^3 = 8 (wbudowane, bez importu)

math.ceil(4.2)          # 5
math.floor(4.8)          # 4
math.trunc(4.8)           # 4 (ucina część po przecinku)
math.factorial(5)          # 120
math.hypot(3, 4)            # 5.0 (twierdzenie Pitagorasa)
```

### `random`

Wszystko *pseudo* — symulacja losowości, nie prawdziwy los.

```python
import random

random.seed(123)             # ustawia ziarno — zawsze ten sam wynik
random.random()                # float 0.0 <= x < 1.0

random.randint(1, 10)           # int z [1, 10]
random.randrange(1, 10)          # int z [1, 10) — prawa strona wykluczona
random.randrange(1, 10, 2)        # co drugi: 1, 3, 5...

random.choice([1, 2, 3])           # losowy jeden element
random.sample([1, 2, 3, 4, 5], 3)   # 3 unikalne elementy
```

### `platform` — informacje o systemie

```python
from platform import *

platform()                   # ogólne info o systemie
machine()                     # np. x86_64
processor()                    # np. Intel i5
system()                        # np. Windows, Linux
version()                        # wersja systemu
python_implementation()           # np. CPython
python_version_tuple()             # ('3', '10', '4')
```

---

## 21. Stringi

- String to **niemodyfikowalna** sekwencja znaków.
- Indeksowanie: `s[0]`, `s[-1]`
- Iteracja: `for c in s:`
- Slicing: `s[2:5]`, `s[::2]`

### Podstawowe operacje

```python
'a' + 'b'      # 'ab' — łączenie
'ab' * 3        # 'ababab' — powielanie
len(s)           # długość
ord(c)            # kod Unicode znaku
chr(n)             # znak o kodzie Unicode n
```

### Metody zwracające nowy string

```python
s.capitalize()          # pierwsza litera duża, reszta małe
s.center(width, ' ')     # centruje do szerokości, wypełnia znakiem
s.lower(); s.upper()      # zmiana wielkości liter
s.swapcase()               # zamienia małe <-> wielkie
s.title()                   # pierwsza litera każdego słowa wielka
s.replace(old, new, count=-1)  # zamienia podłańcuchy
s.strip(); s.lstrip(); s.rstrip()  # usuwa białe znaki (oba/lewa/prawa strona)
s.join(iterable)              # łączy elementy listy separatorem s
s.split(sep=None)              # dzieli string na listę (domyślnie po spacjach)
```

### Wyszukiwanie i sprawdzanie

```python
s.find(sub[, start[, end]])   # indeks pierwszego wystąpienia lub -1
s.rfind(sub)                    # jak find, ale od końca
s.index(sub)                     # jak find, ale rzuca wyjątek jeśli brak
s.rindex(sub)                     # jak index, ale od końca
s.startswith(prefix); s.endswith(suffix)
```

### Metody zwracające bool

```python
s.isalnum()   # litery i cyfry
s.isalpha()    # tylko litery
s.isdigit()     # tylko cyfry
s.islower()      # tylko małe litery
s.isupper()       # tylko wielkie litery
s.isspace()        # tylko białe znaki
```

### Porównywanie i sortowanie

- Porównanie działa znak po znaku wg kodów Unicode; wielkie litery mają mniejszy kod niż małe (`'Z' < 'a'`).
- Nie porównuj stringów z liczbami — błąd.

```python
sorted(list_of_strings)   # zwraca nową posortowaną listę
list.sort()                 # sortuje listę "na miejscu"
```

### Konwersje

```python
str(liczba)      # liczba -> string
int(string)        # string -> int (wymaga poprawnej formy)
float(string)        # string -> float
```

---

## 22. Moduł `datetime`

Zastosowania: logowanie zdarzeń, walidacja danych, przechowywanie dat.

### `date`

```python
from datetime import date

date(year, month, day)     # tworzenie
d.year; d.month; d.day       # atrybuty (tylko do odczytu)
date.today()                   # aktualna data

date.fromtimestamp(time.time())  # data z timestampu (sekundy od 01.01.1970 UTC)
date.fromisoformat("2019-11-04")  # data z formatu ISO YYYY-MM-DD

new_date = d.replace(year=2022)    # zmiana roku/miesiąca/dnia

d.weekday()       # 0=poniedziałek ... 6=niedziela
d.isoweekday()     # 1=poniedziałek ... 7=niedziela
```

### `time`

```python
from datetime import time
time(hour, minute, second, microsecond)   # tworzenie
t.hour; t.minute; t.second; t.microsecond
```

### `datetime`

```python
from datetime import datetime

dt = datetime(year, month, day, hour, minute, second)
dt.year; dt.month; dt.day; dt.hour; dt.minute   # itd.
dt.date(); dt.time()          # osobne obiekty date i time

datetime.today()               # lokalny czas, bez strefy
datetime.now([tz])              # z opcjonalną strefą czasową
datetime.utcnow()                # czas UTC

dt.timestamp()                   # sekundy od epoch (float)
```

### Formatowanie — `strftime()` / `strptime()`

```python
dt.strftime('%Y/%m/%d %H:%M:%S')

dt = datetime.strptime("2019/11/04 14:53:00", "%Y/%m/%d %H:%M:%S")
```

| Dyrektywa | Znaczenie |
|---|---|
| `%Y` | rok czterocyfrowy |
| `%m` | miesiąc (01–12) |
| `%d` | dzień (01–31) |
| `%H %M %S` | godzina, minuta, sekunda |
| `%B` | pełna nazwa miesiąca |
| `%A` | pełna nazwa dnia tygodnia |
| `%j` | dzień roku |
| `%U %W` | numer tygodnia roku |

### `timedelta`

```python
from datetime import timedelta

delta = timedelta(days=10, hours=5)   # różnica między datami/czasami
today = date.today()
next_week = today + timedelta(days=7)  # dodawanie/odejmowanie/mnożenie
```

### Przykłady formatowania

```python
dt = datetime(2020, 11, 4, 14, 53, 0)

dt.strftime("%Y/%m/%d %H:%M:%S")
dt.strftime("%y/%B/%d %H:%M:%S %p")
dt.strftime("%a, %Y %b %d")
dt.strftime("%A, %Y %B %d")
dt.strftime("%w")   # dzień tygodnia
dt.strftime("%j")    # dzień roku
dt.strftime("%U")     # numer tygodnia
```

Podsumowanie: `datetime`, `date`, `time`, `timedelta` to główne klasy; `strftime()` formatuje datę na string, `strptime()` parsuje string na datę.

---

## 23. Moduł `calendar`

```python
import calendar
```

- Dni tygodnia jako liczby: `0=Monday ... 6=Sunday` (stałe: `calendar.MONDAY`, `calendar.SUNDAY` itd.)
- `calendar.calendar(rok)` — tekstowy kalendarz całego roku (parametry `w`, `l`, `c`, `m` do formatowania). Alternatywa: `calendar.prcal(rok)` (bez `print()`).
- `calendar.month(rok, miesiąc)` — kalendarz miesiąca. Alternatywa: `calendar.prmonth(rok, miesiąc)`.
- `calendar.setfirstweekday(n)` — ustawia pierwszy dzień tygodnia (0–6).
- `calendar.weekday(rok, miesiąc, dzień)` — numer dnia tygodnia (0–6) dla podanej daty.
- `calendar.weekheader(szerokość)` — skrócone nazwy dni, np. `weekheader(2)` → `"Mo Tu We Th Fr Sa Su"`.
- `calendar.isleap(rok)` — czy rok przestępny. `calendar.leapdays(start, end)` — liczba lat przestępnych w `[start, end)`.

### Klasy

| Klasa | Opis |
|---|---|
| `Calendar` | klasa bazowa |
| `TextCalendar`, `HTMLCalendar` | kalendarz tekstowy / HTML |
| `LocaleTextCalendar`, `LocaleHTMLCalendar` | wersje z obsługą lokalizacji |

```python
c = calendar.Calendar(firstweekday=0)
c.iterweekdays()   # iterator dni tygodnia od ustawionego pierwszego dnia

calendar.Calendar().itermonthdates(rok, miesiąc)   # wszystkie daty miesiąca jako date, z dopełnieniem tygodni
```

### Inne metody iterujące

```python
c.itermonthdays()      # numery dni miesiąca (0 = dzień spoza miesiąca)
c.itermonthdays2()      # (dzień, dzień_tygodnia) — od Python 3.7
c.itermonthdays3()       # (rok, miesiąc, dzień)
c.itermonthdays4()        # (rok, miesiąc, dzień, dzień_tygodnia)

calendar.monthdays2calendar(rok, miesiąc)  # lista tygodni, każdy = lista krotek (dzień, dzień_tygodnia); dni spoza miesiąca = 0
```
