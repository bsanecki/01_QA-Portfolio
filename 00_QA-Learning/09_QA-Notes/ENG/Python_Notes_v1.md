# Python - Notes

## 1. Data Types

| Type | Description | Example |
|---|---|---|
| `int` | whole numbers (negative, 0, positive) | `5`, `-3`, `1000` |
| `float` | floating-point numbers | `3.14`, `-0.5`, `2.0` |
| `str` | text | `"hello"`, `'Python'` |
| `bool` | logical value (`True`=1, `False`=0) | `True`, `False` |
| `list` | list | `[1, 2, 3]` |
| `tuple` | tuple (immutable) | `(1, 2)` |
| `dict` | dictionary (key: value) | `{"name": "Ala"}` |
| `set` | set (no duplicates) | `{1, 2, 3}` |

```python
print(type(data))          # check the type of a value
b = 4
k = int(b)                 # convert to another type (int, float, str, bool...)
```

### Bool values

```python
print(3 > 15)   # False
print(3 < 15)   # True
```

---

## 2. Input / Output

```python
variable = input()          # user enters a value
print(variable)
```

### `print()` — variants

```python
print("Hello\nworld")                  # Hello / world (new line)
print("Hello", "world", sep="..")      # Hello..world
print("My name is", end="")            # no line-ending character
print("Marek")                         # -> My name is Marek
```

---

## 3. Operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `**` | exponentiation | `2 ** 3` | `8` |
| `*` | multiplication | `2 * 3` | `6` |
| `/` | division | `6 / 2` | `3.0` |
| `//` | integer (floor) division | `7 // 2` | `3` |
| `%` | modulo (remainder) | `7 % 2` | `1` |
| `+` | addition | `2 + 2` | `4` |
| `-` | subtraction | `5 - 3` | `2` |

Concatenating strings: `word = "Foot" + "ball"` → `"Football"`

| Category | Operators | Example |
|---|---|---|
| Arithmetic | `+ - * / % ** //` | `5 + 3 = 8` |
| Assignment | `= += -= *= /=` | `x += 2` → `x = x + 2` |
| Comparison | `== != > < >= <=` | `5 > 3` → `True` |
| Logical | `and or not` | `(x > 0) and (x < 10)` |
| Bitwise | `& \| ^ ~ << >>` | operations on the bits of integers |
| Identity | `is`, `is not` | check whether two variables point to the same object |
| Membership | `in`, `not in` | check whether an element belongs to a collection |

---

## 4. Conditional Statements

```python
age = 18
if age == 18:
    print("Is 18 years old")
elif age > 18:
    print("Is older than 18")
else:
    print("Is a minor")
```

---

## 5. Loops

### `while` — runs while the condition is `True`

```python
number = int(input())
while number <= 5:
    print(number)
    number = number - 1
```

### `for` — runs for each element of a sequence

```python
for i in range(4):
    print("Hello")
# Hello x4
```

---

## 6. Lists

Indexing — positive from the left (starting at 0), negative from the right (starting at -1):

```
index:   0  1  2  3  4  5  6  7  8  9  10 11
L    =   M  o  n  t  y     P  y  t  h  o  n
index:  -12-11-10 -9 -8 -7 -6 -5 -4 -3 -2 -1
```

```python
my_list = [1, None, True, "text", 256, 0]

my_list[1] = "?"            # update the value at an index
print(my_list[3])           # "text"
print(my_list[-1])          # 0 (indexing from the end)

my_list.insert(0, "first")  # insert at the beginning
my_list.append("last")      # append at the end

del my_list[2]               # delete the 3rd element
del my_list                  # delete the whole list

len(my_list)                 # number of elements

list2 = list1                # both variables point to the same list
```

### Slicing

```python
sample = ["A", "B", "C", "D", "E"]

sample[2:-1]     # ['C', 'D']
my_list[2:]      # from the 3rd element to the end
my_list[:2]      # first two
my_list[-2:]     # last two

del my_list[0:2] # delete the first two
del my_list[:]   # clear the whole list
```

### List methods

```python
my_list.reverse()   # reverses the order of elements
my_list.sort()       # sorts the list
my_list.count(x)     # number of occurrences of x
my_list.index(x)     # index of the first occurrence of x
```

### Nested lists

```python
my_list = [1, "a", [2, "b", [3, "c"]]]
print(my_list[2][2][1])   # access to "c"

# only elements outside nested lists
for x in my_list:
    if not isinstance(x, list):
        print(x)
```

---

## 7. Tuples

Cannot be modified once created.

```python
tup = (1, 2, 3)
print(tup[0])   # 1
```

---

## 8. Dictionaries

```python
d = {1: 'a', 2: 'b', 3: 'c'}

d[1]              # 'a'
d[4] = 30          # adds a new key and value
del d[4]           # removes a key

d.keys()           # all keys
d.values()          # all values
d.items()           # (key, value) pairs

# creating a dictionary from two lists
a = [1, 2, 3]
b = ['a', 'b', 'c']
d = dict(zip(a, b))   # {1: 'a', 2: 'b', 3: 'c'}
```

---

## 9. Sets

```python
s = {'a', 'b', 'c'}
set("abcd")          # creates a set from a string, order is arbitrary
s = set()          # empty set

a = {'a', 'b', 'c'}
b = {'c', 'd', 'e'}

a.union(b)                 # a | b     -> a b c d e
a.difference(b)             # a - b     -> what a has that b doesn't
a.intersection(b)           # a & b     -> common elements
a.symmetric_difference(b)   # a ^ b     -> elements NOT shared by both
a.issubset(b)                # whether all elements of a are in b
a.add('w')                   # adds an element to the set
```

---

## 10. Bitwise Operations

Operate at the bit level on integers (`int`).

| Operator | Name | Description | Example |
|---|---|---|---|
| `&` | AND | bits set to 1 in both | `5 & 3` → `1` |
| `\|` | OR | bits set to 1 in either or both | `5 \| 3` → `7` |
| `^` | XOR | bits set to 1 in one, but not both | `5 ^ 3` → `6` |
| `~` | NOT | flips all bits | `~5` → `-6` |
| `<<` | left shift | multiplies by 2ⁿ | `2 << 2` → `8` |
| `>>` | right shift | divides by 2ⁿ (rounded down) | `8 >> 1` → `4` |

---

## 11. Functions

```python
def function_name():
    # function body
    pass

x = 1

def compute():
    global x        # access the global variable
    return x + 1

compute()      # 2

locals()      # all variables in the current scope (e.g. inside a function)
```

---

## 12. Exceptions

```python
x = '10'   # a string, not a number

try:
    x == 5
    print("X equals 5!")
except:
    print("X does not equal 5")
finally:
    print("I always run")   # runs regardless of whether an error occurred
```

### Built-in exceptions

| Exception | Description |
|---|---|
| `BaseException` | the most general exception; all others inherit from it |
| `ArithmeticError` | arithmetic errors, e.g. division by zero |
| `AssertionError` | raised by `assert` when the condition is false |
| `IndexError` | reference to a non-existent index in a sequence |
| `KeyError` | reference to a non-existent key in a dictionary |
| `ImportError` | a module import failed |
| `KeyboardInterrupt` | program interrupted by the user (Ctrl-C) |
| `LookupError` | abstract exception related to invalid lookups in collections |
| `MemoryError` | not enough memory to perform an operation |
| `OverflowError` | result of an arithmetic operation too large to be represented |

### Custom exception

```python
class FileEmptyError(Exception):
    pass
```

---

## 13. Modules

| Term | Description |
|---|---|
| Module | a `.py` file with code (functions, classes, variables) |
| Package | a folder with modules and an `__init__.py` file |
| `__name__` | indicates whether the file is run directly or imported |
| `sys.path` | the list of paths where Python looks for modules |
| `__init__.py` | package initializer file |
| Import from ZIP | modules can be imported from `.zip` archives |

```python
import math                        # import the whole module
from math import sin               # import only the sin function
from math import *                  # import everything from the module
import math as name                # import under a different name
from math import sin as s, pi as PI # import with aliases
```

### Creating your own module

```python
# file name.py contains the function code

import name
name()   # call a function from the module
```

### The special `__name__` variable

```python
__name__ == "__main__"        # when the file is run directly
__name__ == "module_name"     # when the file is imported as a module
```

Lets you test a module when it's run standalone.

### Hiding elements

A `_` or `__` prefix before a variable/function name is a "private" naming convention — it doesn't physically block access, it just signals intent.

### Module paths (`sys.path`)

```python
import sys
sys.path.append('path/to/folder')   # add your own folder to the module search path
```

### Package structure

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

### Basic `pip` commands

| Command | What it does |
|---|---|
| `pip --version` | shows the pip version |
| `pip list` | lists installed packages |
| `pip show <package>` | shows details and dependencies of a package |
| `pip search <string>` | searches PyPI for packages containing a string |
| `pip install <name>` | installs a package globally |
| `pip install --user <name>` | installs a package locally for the current user |
| `pip install -U <name>` | upgrades a package |
| `pip uninstall <name>` | removes a package |

---

## 14. Characters and Encoding

```python
ord(char)    # character -> numeric code
chr(code)    # numeric code -> character
```

- **ASCII** — the base set of 128 characters (codes 0–127); `ord('A') = 65`, `ord('a') = 97` (difference of 32).
- **Unicode** — global character-encoding standard (>1 million characters), the first 128 are ASCII. Python 3 uses Unicode for all `str`.
- **UTF-8** — the default encoding in Python 3, variable length (ASCII = 1 byte, other characters = 2–4 bytes), compatible with ASCII.
- **Code pages** — older, language-dependent encodings, ambiguous — avoid.
- **UCS-4** — 4 bytes per character, less efficient, rarely used.

```python
city = "Łódź"
print(ord('Ł'))   # 321
print(chr(321))   # 'Ł'

with open('file.txt', encoding='utf-8') as f:
    data = f.read()
```

### ASCII table (0–127)

| Char | Code | Char | Code | Char | Code | Char | Code |
|---|---|---|---|---|---|---|---|
| NUL | 0 | space | 32 | @ | 64 | ` | 96 |
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

## 15. Classes (OOP)

### Class definition

```python
class ClassName():
    # class-level code

    def __init__(self, arg1, arg2):   # constructor
        self.arg1 = arg1
        self.arg2 = arg2

    def method(self):
        pass

    def __repr__(self):
        return "ClassName"

    def __str__(self):
        return "object description"

ClassName.__dict__   # all attributes of the class
```

### Class vs. object

- **Class** — a template for an object: attributes and methods.
- **Object** — a specific instance of a class; belongs to its class and all its superclasses.
- `self` — refers to the specific object, the first parameter of every method.

```python
class TheSimplestClass:
    pass

my_first_object = TheSimplestClass()
```

### Inheritance

- A class can have **subclasses**, which inherit from a **superclass**.
- A subclass can override the base class's methods (**override**).
- The base class's constructor must be called manually with `super().__init__()`.

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

### Instance vs. class variables

```python
class Example:
    counter = 0            # class variable — shared by all objects

    def __init__(self):
        Example.counter += 1
        self.instance_var = 123   # instance variable — unique per object
```

Private variables: `__` prefix (name mangling), e.g. `self.__stack_list`.

### Procedural vs. object-oriented (stack example)

```python
# Procedural
stack = []

def push(val):
    stack.append(val)

def pop():
    val = stack[-1]
    del stack[-1]
    return val
# Downside: global list, no encapsulation, only one stack at a time

# Object-oriented
class Stack:
    def __init__(self):
        self.__stack_list = []

    def push(self, val):
        self.__stack_list.append(val)

    def pop(self):
        val = self.__stack_list[-1]
        del self.__stack_list[-1]
        return val
# Advantage: encapsulation, multiple independent stacks, easy to extend
```

### Checking types and inheritance

```python
isinstance(obj, Class)                # whether obj is an instance of Class or its subclass
issubclass(ChildClass, ParentClass)   # whether a class inherits from another
type(obj)                              # returns the object's class
```

Multiple inheritance is possible but requires care (MRO — Method Resolution Order).

---

## 16. Generators, Iterators, Lambdas, Closures

### Iterator

An object implementing:
- `__iter__()` — returns an iterator (usually `self`)
- `__next__()` — returns the next element or raises `StopIteration`

`range()` is a built-in generator.

### `yield`

Works like `return`, but pauses the function and allows it to resume — returns a generator.

```python
def fun(n):
    for i in range(n):
        yield i

def powers_of_2(n):
    power = 1
    for i in range(n):
        yield power
        power *= 2

list(fun(5))   # convert a generator to a list
```

### List comprehension vs. generator expression

```python
[x for x in range(5)]    # returns a list
(x for x in range(5))     # returns a generator (has no len())
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

### `map()` and `filter()`

```python
list(map(lambda x: x * 2, [1, 2, 3]))     # [2, 4, 6]
list(filter(lambda x: x > 0, [-2, 0, 3]))  # [3]
```

### Closures

A function that remembers variables from its enclosing scope, even after the outer function has finished running.

```python
def outer(x):
    def inner(y):
        return x + y
    return inner

add_5 = outer(5)
print(add_5(3))   # 8
```

---

## 17. Files and Streams

```python
stream = open(filename, mode, encoding='utf-8')
stream.close()
```

### File paths

- Windows: `C:\\folder\\file.txt` or `C:/folder/file.txt`
- Linux/Unix: `/home/user/file.txt` (case-sensitive)

### File modes

| Mode | Meaning |
|---|---|
| `r` | read |
| `w` | write (overwrites the file) |
| `a` | append at the end |
| `r+` | read and write, file must exist |
| `w+` | write and read, creates a new file or truncates it |
| `x` | create a new file, error if it exists |
| `+b` | added to a mode → binary mode, e.g. `rb` |
| `t` | text mode (default) |

### Predefined streams

```python
sys.stdin    # standard input (used by input())
sys.stdout   # standard output (used by print())
sys.stderr   # standard error output
```

### Handling I/O errors

```python
errno.ENOENT   # file does not exist
errno.EACCES   # permission denied
os.strerror(errno_code)   # error description
```

### Reading a text file

```python
stream.read(n)        # read n characters
stream.read()          # read the whole file
stream.readline()      # read a single line
stream.readlines()     # return a list of lines

for line in open("file.txt", "rt"):
    print(line, end='')
```

### Writing a text file

```python
# open in mode 'w' (overwrite) or 'a' (append)
stream.write("text\n")   # does not add \n automatically
```

### Binary data

```python
data = bytearray(range(10, 20))
with open("binary.bin", "wb") as f:
    f.write(data)

data = bytearray(10)
with open("binary.bin", "rb") as f:
    f.readinto(data)

# or
with open("binary.bin", "rb") as f:
    data = bytearray(f.read())
```

### Summary of methods

```python
read(n)            # n characters
read()              # the whole file
readline()          # one line
readlines()         # list of lines
readinto(bytearray) # binary data
write(string)        # write text
write(bytearray)     # write binary data
```

---

## 18. The `os` Module

```python
import os

os.uname()      # (Unix) tuple: sysname, nodename, release, version, machine
platform.uname()  # equivalent for Windows

os.name          # 'posix' (Unix/Linux/Mac), 'nt' (Windows), 'java' (Jython)

os.mkdir(path)         # creates a single directory (error if it exists)
os.makedirs(path)       # recursively creates a full directory path
os.listdir([path])      # lists files/directories

os.chdir(path)          # changes the current working directory
os.getcwd()             # returns the current directory path

os.rmdir(path)          # removes an empty directory
os.removedirs(path)     # removes a directory and its empty parent directories

os.system(cmd)          # runs a system command
```

---

## 19. The `time` Module

```python
import time

print("Start")
time.sleep(2)     # pause for 2 seconds
print("Done")

time.time()             # current timestamp (float)
time.ctime([timestamp]) # human-readable date as a string
time.gmtime()             # struct_time (UTC)
time.localtime()          # struct_time (local time)
time.asctime(struct_time) # human-readable date string
time.mktime(struct_time)  # timestamp
time.strftime(fmt[, t])   # format date/time as a string
time.strptime(str, fmt)   # parse a string into struct_time
```

`struct_time` — attributes: `tm_year`, `tm_mon`, `tm_mday`, `tm_hour` ... `tm_isdst`, also accessible as a tuple by index 0–8.

---

## 20. Selected Modules

### `dir()` — module contents

```python
import math
print(dir(math))   # all functions and variables in the module (works after import module_name)
```

### `math`

```python
import math

# trigonometry (radians)
math.sin(x); math.cos(x); math.tan(x)
math.asin(x); math.acos(x); math.atan(x)

math.pi                # constant π
math.radians(180)       # degrees -> radians
math.degrees(x)         # radians -> degrees

math.e                  # Euler's constant
math.exp(x)              # e^x
math.log(x)               # ln(x)
math.log(x, b)             # log base b
math.log10(x); math.log2(x)

pow(2, 3)               # 2^3 = 8 (built-in, no import needed)

math.ceil(4.2)          # 5
math.floor(4.8)          # 4
math.trunc(4.8)           # 4 (truncates the decimal part)
math.factorial(5)          # 120
math.hypot(3, 4)            # 5.0 (Pythagorean theorem)
```

### `random`

Everything is *pseudo* — a simulation of randomness, not true chance.

```python
import random

random.seed(123)             # sets the seed — always the same result
random.random()                # float 0.0 <= x < 1.0

random.randint(1, 10)           # int from [1, 10]
random.randrange(1, 10)          # int from [1, 10) — right side excluded
random.randrange(1, 10, 2)        # every other one: 1, 3, 5...

random.choice([1, 2, 3])           # one random element
random.sample([1, 2, 3, 4, 5], 3)   # 3 unique elements
```

### `platform` — system information

```python
from platform import *

platform()                   # general system info
machine()                     # e.g. x86_64
processor()                    # e.g. Intel i5
system()                        # e.g. Windows, Linux
version()                        # system version
python_implementation()           # e.g. CPython
python_version_tuple()             # ('3', '10', '4')
```

---

## 21. Strings

- A string is an **immutable** sequence of characters.
- Indexing: `s[0]`, `s[-1]`
- Iteration: `for c in s:`
- Slicing: `s[2:5]`, `s[::2]`

### Basic operations

```python
'a' + 'b'      # 'ab' — concatenation
'ab' * 3        # 'ababab' — repetition
len(s)           # length
ord(c)            # Unicode code point of a character
chr(n)             # character for a Unicode code point
```

### Methods that return a new string

```python
s.capitalize()          # first letter uppercase, rest lowercase
s.center(width, ' ')     # centers within a width, padded with a character
s.lower(); s.upper()      # change letter case
s.swapcase()               # swaps lower <-> upper case
s.title()                   # first letter of each word uppercase
s.replace(old, new, count=-1)  # replaces substrings
s.strip(); s.lstrip(); s.rstrip()  # removes whitespace (both/left/right)
s.join(iterable)              # joins list elements using s as separator
s.split(sep=None)              # splits a string into a list (default: on spaces)
```

### Searching and checking

```python
s.find(sub[, start[, end]])   # index of the first occurrence or -1
s.rfind(sub)                    # like find, but from the end
s.index(sub)                     # like find, but raises an exception if not found
s.rindex(sub)                     # like index, but from the end
s.startswith(prefix); s.endswith(suffix)
```

### Methods that return a bool

```python
s.isalnum()   # letters and digits
s.isalpha()    # letters only
s.isdigit()     # digits only
s.islower()      # lowercase letters only
s.isupper()       # uppercase letters only
s.isspace()        # whitespace only
```

### Comparing and sorting

- Comparison works character by character based on Unicode code points; uppercase letters have a lower code than lowercase (`'Z' < 'a'`).
- Don't compare strings with numbers — this causes an error.

```python
sorted(list_of_strings)   # returns a new sorted list
list.sort()                 # sorts the list in place
```

### Conversions

```python
str(number)      # number -> string
int(string)        # string -> int (requires a valid format)
float(string)        # string -> float
```

---

## 22. The `datetime` Module

Uses: event logging, data validation, storing dates (e.g. transactions).

### `date` object

```python
from datetime import date

date(year, month, day)     # creation
d.year; d.month; d.day       # attributes (read-only)
date.today()                   # current date

date.fromtimestamp(time.time())  # date from a timestamp (seconds since 01.01.1970 UTC)
date.fromisoformat("2019-11-04")  # date from ISO format YYYY-MM-DD

new_date = d.replace(year=2022)    # change the year/month/day

d.weekday()       # 0=Monday ... 6=Sunday
d.isoweekday()     # 1=Monday ... 7=Sunday
```

### `time` object

```python
from datetime import time
time(hour, minute, second, microsecond)   # creation
t.hour; t.minute; t.second; t.microsecond
```

### `datetime` object

```python
from datetime import datetime

dt = datetime(year, month, day, hour, minute, second)
dt.year; dt.month; dt.day; dt.hour; dt.minute   # etc.
dt.date(); dt.time()          # separate date and time objects

datetime.today()               # local time, no timezone
datetime.now([tz])              # with an optional timezone
datetime.utcnow()                # UTC time

dt.timestamp()                   # seconds since epoch (float)
```

### Formatting — `strftime()` / `strptime()`

```python
dt.strftime('%Y/%m/%d %H:%M:%S')

dt = datetime.strptime("2019/11/04 14:53:00", "%Y/%m/%d %H:%M:%S")
```

| Directive | Meaning |
|---|---|
| `%Y` | 4-digit year |
| `%m` | month (01–12) |
| `%d` | day (01–31) |
| `%H %M %S` | hour, minute, second |
| `%B` | full month name |
| `%A` | full weekday name |
| `%j` | day of the year |
| `%U %W` | week number of the year |

### `timedelta`

```python
from datetime import timedelta

delta = timedelta(days=10, hours=5)   # difference between dates/times
today = date.today()
next_week = today + timedelta(days=7)  # add/subtract/multiply
```

### Formatting examples

```python
dt = datetime(2020, 11, 4, 14, 53, 0)

dt.strftime("%Y/%m/%d %H:%M:%S")
dt.strftime("%y/%B/%d %H:%M:%S %p")
dt.strftime("%a, %Y %b %d")
dt.strftime("%A, %Y %B %d")
dt.strftime("%w")   # weekday
dt.strftime("%j")    # day of the year
dt.strftime("%U")     # week number
```

Summary: `datetime`, `date`, `time`, `timedelta` are the main classes; `strftime()` formats a date/time into a string, `strptime()` parses a string into a date/time.

---

## 23. The `calendar` Module

```python
import calendar
```

- Weekdays as numbers: `0=Monday ... 6=Sunday` (constants: `calendar.MONDAY`, `calendar.SUNDAY`, etc.)
- `calendar.calendar(year)` — a full-year text calendar (parameters `w`, `l`, `c`, `m` for formatting). Alternative: `calendar.prcal(year)` (no `print()` needed).
- `calendar.month(year, month)` — a calendar for a given month. Alternative: `calendar.prmonth(year, month)`.
- `calendar.setfirstweekday(n)` — sets the first day of the week (0–6).
- `calendar.weekday(year, month, day)` — returns the weekday number (0–6) for a given date.
- `calendar.weekheader(width)` — abbreviated weekday names, e.g. `weekheader(2)` → `"Mo Tu We Th Fr Sa Su"`.
- `calendar.isleap(year)` — whether the year is a leap year. `calendar.leapdays(start, end)` — number of leap years in `[start, end)`.

### Classes

| Class | Description |
|---|---|
| `Calendar` | base class |
| `TextCalendar`, `HTMLCalendar` | text or HTML calendars |
| `LocaleTextCalendar`, `LocaleHTMLCalendar` | localization-aware versions |

```python
c = calendar.Calendar(firstweekday=0)
c.iterweekdays()   # an iterator of weekdays starting from the configured first day

calendar.Calendar().itermonthdates(year, month)   # all dates of the month as date objects, padded to full weeks
```

### Other iterating methods

```python
c.itermonthdays()      # day numbers of the month (0 = day outside the month)
c.itermonthdays2()      # (day, weekday) — since Python 3.7
c.itermonthdays3()       # (year, month, day)
c.itermonthdays4()        # (year, month, day, weekday)

calendar.monthdays2calendar(year, month)  # list of weeks, each a list of (day, weekday) tuples; days outside the month = 0
```
