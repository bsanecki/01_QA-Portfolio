# Python - Requests, Web Scraping, JSON, Pandas, Matplotlib/Seaborn

Kolejność tematyczna: pobieranie danych z sieci (`requests`) → wyciąganie danych ze stron (`BeautifulSoup`, `Selenium`) → zapis/odczyt danych (`json`) → analiza danych (`pandas`) → wizualizacja danych (`matplotlib`, `seaborn`).

---

# CZĘŚĆ I - `requests` (HTTP)

## 1. Podstawowe metody HTTP

**GET - pobieranie danych**

```python
response = requests.get('https://jsonplaceholder.typicode.com/posts')
print(response.status_code)  # 200 = OK
print(response.text)         # surowa odpowiedź jako tekst
print(response.json())       # dane w formacie JSON jako Python
```

**POST - wysyłanie danych**

```python
data = {'title': 'Hello', 'body': 'Test', 'userId': 1}
response = requests.post('https://jsonplaceholder.typicode.com/posts', json=data)
print(response.json())
```

## 2. Odczyt odpowiedzi

```python
response = requests.get(url)

# Status
response.status_code   # np. 200, 404, 500
response.ok             # True jeśli status 200–299

# Treść
response.text            # surowy tekst HTML/JSON/XML
response.json()           # zamienia JSON -> Python (słownik/lista)
response.content           # dane binarne (np. do pobierania plików)
```

## 3. Wysyłanie danych

```python
# params — dodanie parametrów do URL
params = {'userId': 1}
response = requests.get('https://jsonplaceholder.typicode.com/posts', params=params)
# wysyła żądanie np. na: https://.../posts?userId=1

# data — formularze (x-www-form-urlencoded)
data = {'username': 'admin', 'password': '1234'}
response = requests.post('https://example.com/login', data=data)

# json — wysyłanie danych jako JSON
payload = {'name': 'John'}
response = requests.post('https://example.com/api', json=payload)
```

## 4. Obsługa błędów

```python
response = requests.get(url)

if response.status_code == 200:
    print("OK")
else:
    print("Błąd:", response.status_code)
```

```python
response.raise_for_status()   # rzuci wyjątek dla błędów 4xx / 5xx
```

## 5. Nagłówki (`headers`)

```python
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Authorization': 'Bearer TOKEN'
}
response = requests.get(url, headers=headers)
```

Serwery często sprawdzają, kto się łączy z ich stroną. Nagłówek `User-Agent` mówi im, że to np. przeglądarka Firefox lub własna aplikacja — dzięki temu można uniknąć blokad albo dostać wersję strony dla prawdziwego użytkownika.

```python
requests.get(url, headers={'User-Agent': 'MojaAplikacja/1.0'})
```

## 6. Autoryzacja (Basic Auth)

```python
from requests.auth import HTTPBasicAuth
response = requests.get('https://example.com', auth=HTTPBasicAuth('user', 'pass'))

# lub krócej
response = requests.get('https://example.com', auth=('user', 'pass'))
```

## 7. Pobieranie plików

```python
url = 'https://example.com/image.jpg'
response = requests.get(url)

with open('image.jpg', 'wb') as f:
    f.write(response.content)
```

---

# CZĘŚĆ II - Web scraping

## 1. BeautifulSoup - statyczne strony

Biblioteka do "czytania" i "rozumienia" kodu HTML stron internetowych. Umożliwia wyciąganie konkretnych informacji ze statycznych stron (teksty, linki, nagłówki, ceny itp.).

### Instalacja

```bash
pip install beautifulsoup4 requests
```

### Pełny przykład: pobieranie tytułu strony i linków

```python
import requests                    # pobieranie stron z internetu
from bs4 import BeautifulSoup      # parser HTML do czytania struktury strony

# 1. Adres strony, którą chcemy pobrać
url = 'https://example.com'

# 2. Wysyłamy żądanie GET do serwera i pobieramy odpowiedź (HTML)
response = requests.get(url)

# 3. Parsujemy odpowiedź jako HTML
soup = BeautifulSoup(response.text, 'html.parser')  # zamienia tekst na obiekt do przeszukiwania

# 4. Pobieramy tytuł strony (element <title>)
print("Tytuł strony:", soup.title.text)  # wyświetla tytuł, np. "Example Domain"

# 5. Pobieramy wszystkie linki na stronie (elementy <a>)
linki = soup.find_all('a')  # szuka wszystkich elementów <a>

print("Znalezione linki:")
for link in linki:
    print(link['href'])  # wypisuje adres z atrybutu href
```

### Przykład: pobieranie nazw produktów i cen z HTML-a

```python
html = """
<html>
<body>
    <div class="product">
        <h2>Produkt A</h2>
        <span class="price">100 zł</span>
    </div>
    <div class="product">
        <h2>Produkt B</h2>
        <span class="price">150 zł</span>
    </div>
</body>
</html>
"""

from bs4 import BeautifulSoup

# Tworzymy obiekt BeautifulSoup z przykładowego HTML-a
soup = BeautifulSoup(html, 'html.parser')

# Szukamy wszystkich divów z klasą 'product'
produkty = soup.find_all('div', class_='product')

for p in produkty:
    nazwa = p.find('h2').text                      # pobiera tekst z elementu <h2>
    cena = p.find('span', class_='price').text      # pobiera tekst z <span class='price'>
    print(f"{nazwa} kosztuje {cena}")
```

### Ważne metody BeautifulSoup

| Kod | Znaczenie |
|---|---|
| `soup.find('tag')` | zwraca pierwszy pasujący tag, np. `div`, `a` |
| `soup.find_all('tag')` | zwraca listę wszystkich pasujących tagów |
| `soup.find('tag', class_='x')` | szuka po nazwie klasy CSS |
| `element.text` | zwraca tekst wewnątrz HTML-a |
| `element['href']` | zwraca wartość atrybutu (np. link) |
| `soup.select('div.product > h2')` | szukanie elementów po selektorze CSS |

## 2. Selenium — strony dynamiczne (JavaScript)

Narzędzie pozwalające sterować prawdziwą przeglądarką internetową za pomocą Pythona. Umożliwia klikanie, wpisywanie tekstu, przewijanie stron i pobieranie danych ze stron dynamicznych korzystających z JavaScriptu.

### Instalacja

```bash
pip install selenium
```

Potrzebny jest też **ChromeDriver** (dla przeglądarki Chrome) — pobrany plik zapisujemy np. w tym samym folderze co skrypt.

### Przykład: otwarcie strony i pobranie nagłówka

```python
from selenium import webdriver                          # biblioteka do automatyzacji przeglądarki
from selenium.webdriver.common.by import By              # do wskazywania elementów np. po klasie, tagu
from selenium.webdriver.chrome.service import Service    # do ustawienia ścieżki do chromedrivera

# 1. Ścieżka do lokalnego pliku ChromeDriver
service = Service('chromedriver.exe')  # jeśli plik w tym samym folderze

# 2. Tworzymy obiekt przeglądarki Chrome
driver = webdriver.Chrome(service=service)

# 3. Otwieramy stronę
driver.get("https://example.com")  # ładuje stronę w przeglądarce

# 4. Szukamy elementu <h1> i pobieramy jego tekst
naglowek = driver.find_element(By.TAG_NAME, "h1")  # szuka <h1>
print("Tytuł strony to:", naglowek.text)

# 5. Zamykamy przeglądarkę
driver.quit()
```

### Przykład: pobieranie listy produktów (strona dynamiczna)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Uruchamiamy przeglądarkę
service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Przechodzimy do strony z produktami (np. sklep)
driver.get('https://example.com/produkty')

# Szukamy wielu elementów z klasą "product"
produkty = driver.find_elements(By.CLASS_NAME, 'product')

for p in produkty:
    print(p.text)  # wypisuje cały tekst z każdego produktu (nazwa, cena)

# Zamykamy przeglądarkę
driver.quit()
```

### Przykład: kliknięcie przycisku i wpisanie tekstu

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

driver.get("https://google.com")

# Akceptacja ciasteczek (jeśli przycisk istnieje)
try:
    zgoda = driver.find_element(By.ID, 'L2AGLb')
    zgoda.click()
except:
    pass

# Szukamy pola tekstowego i wpisujemy zapytanie
pole = driver.find_element(By.NAME, 'q')
pole.send_keys('Python')       # wpisuje "Python"
pole.send_keys(Keys.RETURN)    # naciska Enter

time.sleep(3)  # czekamy, aż załadują się wyniki

# Pobieramy tytuły wyników
tytuly = driver.find_elements(By.TAG_NAME, 'h3')
for t in tytuly:
    print(t.text)

driver.quit()
```

### Scrollowanie strony

```python
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

Przewija stronę automatycznie na sam dół — jakby użytkownik przesunął pasek przewijania myszką lub palcem.

### Screenshoty (zrzuty ekranu)

```python
driver.save_screenshot('screen.png')
```

Robi zdjęcie aktualnie widocznej strony w przeglądarce i zapisuje je jako plik `screen.png`. Przydatne, gdy trzeba zachować obraz strony albo sprawdzić, czy scraper działa poprawnie.

## 3. Zapis wyników do CSV

```python
import csv

produkty = [
    ['Produkt A', '100 zł'],
    ['Produkt B', '150 zł']
]

with open('produkty.csv', 'w', newline='', encoding='utf-8') as plik:
    writer = csv.writer(plik)
    writer.writerow(['Nazwa', 'Cena'])  # nagłówki
    writer.writerows(produkty)           # dane
```

---

# CZĘŚĆ III - `json`

Python ma wbudowaną bibliotekę `json`, dzięki której można łatwo zapisywać dane do pliku `.json` i je z niego odczytywać.

### Zapis do pliku `.json`

```python
import json

dane = {
    "imie": "Kasia",
    "wiek": 25,
    "czy_programuje": True
}

with open("uzytkownik.json", "w") as plik:
    json.dump(dane, plik)
```

### Odczyt z pliku `.json`

```python
import json

with open("uzytkownik.json", "r") as plik:
    dane = json.load(plik)

print(dane["imie"])  # -> Kasia
```

---

# CZĘŚĆ IV - Pandas

```python
import pandas as pd              # importuje bibliotekę pandas

arkusz = pd.DataFrame()          # tworzy pusty arkusz DataFrame
```

## 1. Tworzenie i dodawanie kolumn

```python
arkusz['color'] = ['blue', 'red', 'yellow', 'green']
arkusz['radius'] = [2, 4, 3, 5]                       # dodawanie kolumn
arkusz['diameter'] = arkusz['radius'] * 2              # nowa kolumna z wartością *2
```

## 2. Statystyki kolumn

```python
arkusz['radius'].min()      # minimalna wartość w kolumnie 'radius'
arkusz['diameter'].sum()     # suma wartości w kolumnie 'diameter'
arkusz['radius'].mean()       # średnia wartość w kolumnie 'radius'
```

## 3. Odczyt danych

```python
arkusz['color']       # pokazuje daną kolumnę

arkusz.iloc[0]          # pierwszy wiersz
arkusz.iloc[-1]          # ostatni wiersz

arkusz.columns            # nazwy kolumn w arkuszu
arkusz.index                # indeksy wierszy w arkuszu
arkusz.shape                  # kształt arkusza (wiersze, kolumny)

arkusz.head(5)                  # pierwsze 5 wierszy
arkusz.tail(5)                    # ostatnie 5 wierszy
arkusz.info()                       # podstawowe informacje o arkuszu
```

## 4. Wczytywanie danych z pliku

```python
zaladowany_arkusz = pd.read_csv('earth-layers.csv')   # ładowanie arkusza z CSV
```

## 5. Operacje i filtrowanie danych

```python
arkusz['area'] = arkusz.eval('0.5 * base * height')   # operacja na danych kolumn

arkusz.query('wartosc > 30')             # tylko wartości większe od 30
arkusz.query('wartosc == days.min()')     # tylko najmniejsza wartość w kolumnie
```

## 6. Grupowanie danych

```python
groups = arkusz.groupby('kolumna')     # grupuje dane wg wybranej kolumny
groups['weight'].mean()                  # średnia dla danej kolumny w grupach

series.reset_index()   # przywraca arkusz do wyglądu sprzed groupby

arkusz['region'].value_counts()   # zlicza wartości w kolumnie (np. Pies:3, kot:2, kuna:1)
```

## 7. Dzielenie kolumny tekstowej na części

```python
import pandas as pd

# Przykładowy arkusz danych
data = {'duration': ['02:35:19', '03:45:10', '01:20:45', '04:10:30']}
arkusz = pd.DataFrame(data)

# Dzielimy wartości w kolumnie 'duration' na części (godziny, minuty, sekundy)
split_duration = arkusz['duration'].str.split(':', expand=True)

# Zamieniamy wartości na typ całkowity
split_duration = split_duration.astype('int')

# Przypisujemy kolumny h, m, s do głównego arkusza
arkusz[['h', 'm', 's']] = split_duration
```

## 8. Braki danych

```python
arkusz.dropna()          # usuwa puste miejsca z arkusza
arkusz.isna().sum()        # ile jest pustych miejsc w arkuszu (na kolumnę)
```

## 9. Wybieranie konkretnych kolumn

```python
dane = {
    'timestamp': ['2023-09-01', '2023-09-02', '2023-09-03'],
    'age': [25, 30, 22],
    'cow_milk': [1, 0, 1],
    'almond_milk': [0, 1, 1],
    'oat_milk': [1, 0, 0],
    'gender': ['F', 'M', 'F']
}

survey = pd.DataFrame(dane)

# Definiujemy tylko kolumny, które nas interesują (mleczne)
needed_columns = ['cow_milk', 'almond_milk', 'oat_milk']

# Nowy arkusz tylko z tymi kolumnami
arkusz = survey[needed_columns]
```

## 10. Modyfikacja wierszy i kolumn

```python
arkusz.loc['ref_0'] = ['submarine implosion', 730, 'C1']   # nowy wiersz z podanymi wartościami

arkusz = arkusz.rename(columns={'stara': 'nowa'})   # zmiana nazwy kolumny
```

---

# CZĘŚĆ V - Matplotlib i Seaborn

## 1. Matplotlib - podstawy

```python
import matplotlib.pyplot as plt   # import biblioteki
```

### Rodzaje wykresów

```python
a = [1, 2, 3, 4]
b = [1, 4, 3, 4]
plt.plot(a, b)      # wykres liniowy (line plot)

a = ['A', 'B', 'C']
b = [4, 1, 2]
plt.bar(a, b)         # wykres słupkowy (bar chart)
plt.barh(a, b)          # poziomy wykres słupkowy (horizontal bar chart)

a = [1, 2, 3, 4]
b = [1, 4, 3, 4]
plt.scatter(a, b)         # wykres punktowy (scatter plot)
```

### Dane z arkusza + opisywanie wykresu

```python
x = arkusz['kolumna_1']
y = arkusz['kolumna_2']

plt.bar(x, y)                            # wykres z danych z arkusza
plt.ylabel('wartosc osi y')               # nazwa osi y
plt.title('Tytuł wykresu!')                # tytuł wykresu
plt.legend()                                # wyświetla legendę
```

### Formatowanie i układ

```python
df['color'] = 'C0'                                              # kolor dla wszystkich wierszy
ax.grid(True, axis='x', linestyle='--', alpha=0.7)                # siatka na osi x
ax.tick_params(left=False, bottom=False)                            # wyłącza ticki
plt.tight_layout()                                                    # elementy się nie nakładają
format_axes()                                                           # formatuje osie

plt.xlim(1960, 1990)   # ogranicza zakres danych do podanych wartości

arkusz.savefig('nazwa')   # zapisuje wykres pod podaną nazwą
arkusz.show()               # wyświetla wykres
```

### Modele (regresja)

```python
LinearModel()       # tworzy liniowy model wykresu
QuadraticModel()      # tworzy model kwadratowy wykresu (y = x² + 3b + 1)
```

### Zmiana koloru, stylu linii i markerów

```python
plt.plot(x, y, 'r--o')
# 'r'  = czerwony kolor (red)
# '--' = przerywana linia (dashed)
# 'o'  = marker w kształcie kółka
plt.title('Wykres z czerwonymi przerywanymi liniami i kółkami')
plt.show()
```

### Wykresy wielopanelowe (subplots)

```python
plt.figure(figsize=(10, 4))   # rozmiar figury (szerokość, wysokość)

plt.subplot(1, 2, 1)   # 1 wiersz, 2 kolumny, pierwszy wykres
plt.plot(x, y)
plt.title('Wykres 1')

plt.subplot(1, 2, 2)   # 1 wiersz, 2 kolumny, drugi wykres
plt.bar(x, y)
plt.title('Wykres 2')

plt.tight_layout()   # żeby wykresy się nie nakładały
plt.show()
```

### Skala logarytmiczna osi Y

```python
plt.plot(x, y)
plt.yscale('log')   # zmienia oś Y na logarytmiczną
plt.title('Wykres z logarytmiczną osią Y')
plt.show()
```

### Rotacja etykiet na osi X

Przydaje się, gdy etykiety są długie i się nakładają:

```python
plt.bar(x, y)
plt.xticks(rotation=45)   # obraca etykiety osi X o 45 stopni
plt.show()
```

### Zmiana rozmiaru wykresu

```python
plt.figure(figsize=(8, 6))   # rozmiar wykresu: 8 cali szerokości, 6 cali wysokości
plt.plot(x, y)
plt.show()
```

## 2. Seaborn — ładniejsze wykresy

```python
import seaborn as sns
import matplotlib.pyplot as plt   # seaborn działa na matplotlib, więc to też potrzebne
```

### Podstawowe funkcje

```python
sns.barplot(x, y, data=...)        # wykres słupkowy z automatycznym agregowaniem (średnia, odchylenie)
sns.scatterplot(x, y, data=...)     # wykres punktowy (scatter)
sns.lineplot(x, y, data=...)          # wykres liniowy
sns.histplot(data, x=..., bins=...)     # histogram
sns.boxplot(x, y, data=...)               # wykres pudełkowy (analiza rozkładu, wykrywanie outlierów)
sns.heatmap(data)                           # mapa cieplna (np. korelacje)
```

### Przykłady

```python
# Wykres słupkowy
sns.barplot(x='kolumna_1', y='kolumna_2', data=arkusz)
plt.title('Wykres słupkowy seaborn')
plt.show()

# Wykres punktowy z kolorem wg kategorii
sns.scatterplot(x='wiek', y='zarobki', hue='płeć', data=arkusz)
plt.title('Zarobki wg wieku i płci')
plt.show()
```
