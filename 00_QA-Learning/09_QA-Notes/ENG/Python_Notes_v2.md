# Python - Requests, Web Scraping, JSON, Pandas, Matplotlib/Seaborn

Topic order: fetching data from the web (`requests`) -> extracting data from pages (`BeautifulSoup`, `Selenium`) -> saving/loading data (`json`) -> analyzing data (`pandas`) -> visualizing data (`matplotlib`, `seaborn`).

---

# PART I - `requests` (HTTP)

## 1. Basic HTTP methods

**GET - fetching data**

```python
response = requests.get('https://jsonplaceholder.typicode.com/posts')
print(response.status_code)  # 200 = OK
print(response.text)         # raw response as text
print(response.json())       # JSON data as Python
```

**POST - sending data**

```python
data = {'title': 'Hello', 'body': 'Test', 'userId': 1}
response = requests.post('https://jsonplaceholder.typicode.com/posts', json=data)
print(response.json())
```

## 2. Reading the response

```python
response = requests.get(url)

# Status
response.status_code   # e.g. 200, 404, 500
response.ok             # True if status is 200-299

# Content
response.text            # raw text HTML/JSON/XML
response.json()           # converts JSON -> Python (dict/list)
response.content           # binary data (e.g. for downloading files)
```

## 3. Sending data

```python
# params - adding parameters to the URL
params = {'userId': 1}
response = requests.get('https://jsonplaceholder.typicode.com/posts', params=params)
# sends a request e.g. to: https://.../posts?userId=1

# data - forms (x-www-form-urlencoded)
data = {'username': 'admin', 'password': '1234'}
response = requests.post('https://example.com/login', data=data)

# json - sending data as JSON
payload = {'name': 'John'}
response = requests.post('https://example.com/api', json=payload)
```

## 4. Error handling

```python
response = requests.get(url)

if response.status_code == 200:
    print("OK")
else:
    print("Error:", response.status_code)
```

```python
response.raise_for_status()   # raises an exception for 4xx / 5xx errors
```

## 5. Headers (`headers`)

```python
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Authorization': 'Bearer TOKEN'
}
response = requests.get(url, headers=headers)
```

Servers often check who is connecting to them. The `User-Agent` header tells them it's e.g. Firefox or a custom app - this can help avoid blocks or get the version of the page meant for real users.

```python
requests.get(url, headers={'User-Agent': 'MyApp/1.0'})
```

## 6. Authorization (Basic Auth)

```python
from requests.auth import HTTPBasicAuth
response = requests.get('https://example.com', auth=HTTPBasicAuth('user', 'pass'))

# or shorter
response = requests.get('https://example.com', auth=('user', 'pass'))
```

## 7. Downloading files

```python
url = 'https://example.com/image.jpg'
response = requests.get(url)

with open('image.jpg', 'wb') as f:
    f.write(response.content)
```

---

# PART II - Web scraping

## 1. BeautifulSoup - static pages

A library for "reading" and "understanding" the HTML code of web pages. Lets you easily find and extract specific information from static pages - text, links, headings, prices, etc.

### Installation

```bash
pip install beautifulsoup4 requests
```

### Full example: getting the page title and links

```python
import requests                    # for downloading pages from the internet
from bs4 import BeautifulSoup      # HTML parser for reading page structure

# 1. The address of the page we want to download
url = 'https://example.com'

# 2. Send a GET request to the server and get the response (HTML)
response = requests.get(url)

# 3. Parse the response as HTML
soup = BeautifulSoup(response.text, 'html.parser')  # turns the text into a searchable object

# 4. Get the page title (the <title> element)
print("Page title:", soup.title.text)  # shows the title, e.g. "Example Domain"

# 5. Get all links on the page (the <a> elements)
links = soup.find_all('a')  # finds all <a> elements

print("Links found:")
for link in links:
    print(link['href'])  # prints the address from the href attribute
```

### Example: getting product names and prices from HTML

```python
html = """
<html>
<body>
    <div class="product">
        <h2>Product A</h2>
        <span class="price">$100</span>
    </div>
    <div class="product">
        <h2>Product B</h2>
        <span class="price">$150</span>
    </div>
</body>
</html>
"""

from bs4 import BeautifulSoup

# Create a BeautifulSoup object from the sample HTML
soup = BeautifulSoup(html, 'html.parser')

# Find all divs with the class 'product'
products = soup.find_all('div', class_='product')

for p in products:
    name = p.find('h2').text                        # gets the text from the <h2> element
    price = p.find('span', class_='price').text      # gets the text from <span class='price'>
    print(f"{name} costs {price}")
```

### Important BeautifulSoup methods

| Code | Meaning |
|---|---|
| `soup.find('tag')` | returns the first matching tag, e.g. `div`, `a` |
| `soup.find_all('tag')` | returns a list of all matching tags |
| `soup.find('tag', class_='x')` | searches by CSS class name |
| `element.text` | returns the text inside the HTML element |
| `element['href']` | returns the value of an attribute (e.g. a link) |
| `soup.select('div.product > h2')` | finds elements using a CSS selector |

## 2. Selenium - dynamic pages (JavaScript)

A tool that lets you control a real web browser from Python. It allows clicking, typing text, scrolling pages, and pulling data from dynamic pages that use JavaScript.

### Installation

```bash
pip install selenium
```

You also need **ChromeDriver** (for the Chrome browser) - save the downloaded file, e.g. in the same folder as your script.

### Example: opening a page and getting its heading

```python
from selenium import webdriver                          # library for browser automation
from selenium.webdriver.common.by import By              # for locating elements, e.g. by class, tag
from selenium.webdriver.chrome.service import Service    # for setting the path to chromedriver

# 1. Path to the local ChromeDriver file
service = Service('chromedriver.exe')  # if the file is in the same folder

# 2. Create a Chrome browser object
driver = webdriver.Chrome(service=service)

# 3. Open the page
driver.get("https://example.com")  # loads the page in the browser

# 4. Find the <h1> element and get its text
heading = driver.find_element(By.TAG_NAME, "h1")  # finds <h1>
print("Page title is:", heading.text)

# 5. Close the browser
driver.quit()
```

### Example: getting a list of products (dynamic page)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Launch the browser
service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Go to a page with products (e.g. a shop)
driver.get('https://example.com/products')

# Find multiple elements with the class "product"
products = driver.find_elements(By.CLASS_NAME, 'product')

for p in products:
    print(p.text)  # prints the full text of each product (name, price)

# Close the browser
driver.quit()
```

### Example: clicking a button and typing text

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

driver.get("https://google.com")

# Accept cookies (if the button exists)
try:
    consent = driver.find_element(By.ID, 'L2AGLb')
    consent.click()
except:
    pass

# Find the text field and type a query
field = driver.find_element(By.NAME, 'q')
field.send_keys('Python')       # types "Python"
field.send_keys(Keys.RETURN)    # presses Enter

time.sleep(3)  # wait for the results to load

# Get the result titles
titles = driver.find_elements(By.TAG_NAME, 'h3')
for t in titles:
    print(t.text)

driver.quit()
```

### Scrolling the page

```python
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

Automatically scrolls the page all the way down - as if the user dragged the scrollbar or swiped down.

### Screenshots

```python
driver.save_screenshot('screen.png')
```

Takes a picture of the currently visible page in the browser and saves it as `screen.png`. Useful when you need to keep a record of the page or check whether the scraper is working correctly.

## 3. Saving results to CSV

```python
import csv

products = [
    ['Product A', '$100'],
    ['Product B', '$150']
]

with open('products.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Price'])  # headers
    writer.writerows(products)           # data
```

---

# PART III - `json`

Python has a built-in `json` library that makes it easy to save data to a `.json` file and read it back.

### Writing to a `.json` file

```python
import json

data = {
    "name": "Kate",
    "age": 25,
    "is_programmer": True
}

with open("user.json", "w") as file:
    json.dump(data, file)
```

### Reading from a `.json` file

```python
import json

with open("user.json", "r") as file:
    data = json.load(file)

print(data["name"])  # -> Kate
```

---

# PART IV - Pandas

```python
import pandas as pd              # import the pandas library

df = pd.DataFrame()          # creates an empty DataFrame
```

## 1. Creating and adding columns

```python
df['color'] = ['blue', 'red', 'yellow', 'green']
df['radius'] = [2, 4, 3, 5]                       # adding columns
df['diameter'] = df['radius'] * 2              # new column with the value *2
```

## 2. Column statistics

```python
df['radius'].min()      # minimum value in the 'radius' column
df['diameter'].sum()     # sum of values in the 'diameter' column
df['radius'].mean()       # average value in the 'radius' column
```

## 3. Reading data

```python
df['color']       # shows a given column

df.iloc[0]          # first row
df.iloc[-1]          # last row

df.columns            # column names in the dataframe
df.index                # row indexes in the dataframe
df.shape                  # shape of the dataframe (rows, columns)

df.head(5)                  # first 5 rows
df.tail(5)                    # last 5 rows
df.info()                       # basic information about the dataframe
```

## 4. Loading data from a file

```python
loaded_df = pd.read_csv('earth-layers.csv')   # loading a dataframe from CSV
```

## 5. Operations and filtering data

```python
df['area'] = df.eval('0.5 * base * height')   # operation on column data

df.query('value > 30')             # only values greater than 30
df.query('value == days.min()')     # only the smallest value in the column
```

## 6. Grouping data

```python
groups = df.groupby('column')     # groups data by the chosen column
groups['weight'].mean()             # average for a given column within groups

series.reset_index()   # restores the dataframe to how it looked before groupby

df['region'].value_counts()   # counts values in a column (e.g. Dog:3, Cat:2, Marten:1)
```

## 7. Splitting a text column into parts

```python
import pandas as pd

# Sample dataframe
data = {'duration': ['02:35:19', '03:45:10', '01:20:45', '04:10:30']}
df = pd.DataFrame(data)

# Split the values in the 'duration' column into parts (hours, minutes, seconds)
split_duration = df['duration'].str.split(':', expand=True)

# Convert the values to integer type
split_duration = split_duration.astype('int')

# Assign the h, m, s columns to the main dataframe
df[['h', 'm', 's']] = split_duration
```

## 8. Missing data

```python
df.dropna()          # removes empty spots from the dataframe
df.isna().sum()        # how many empty spots there are in the dataframe (per column)
```

## 9. Selecting specific columns

```python
data = {
    'timestamp': ['2023-09-01', '2023-09-02', '2023-09-03'],
    'age': [25, 30, 22],
    'cow_milk': [1, 0, 1],
    'almond_milk': [0, 1, 1],
    'oat_milk': [1, 0, 0],
    'gender': ['F', 'M', 'F']
}

survey = pd.DataFrame(data)

# Define only the columns we're interested in (dairy-related)
needed_columns = ['cow_milk', 'almond_milk', 'oat_milk']

# New dataframe with only these columns
df = survey[needed_columns]
```

## 10. Modifying rows and columns

```python
df.loc['ref_0'] = ['submarine implosion', 730, 'C1']   # new row with the given values

df = df.rename(columns={'old': 'new'})   # renaming a column
```

---

# PART V - Matplotlib and Seaborn

## 1. Matplotlib - basics

```python
import matplotlib.pyplot as plt   # import the library
```

### Chart types

```python
a = [1, 2, 3, 4]
b = [1, 4, 3, 4]
plt.plot(a, b)      # line plot

a = ['A', 'B', 'C']
b = [4, 1, 2]
plt.bar(a, b)         # bar chart
plt.barh(a, b)          # horizontal bar chart

a = [1, 2, 3, 4]
b = [1, 4, 3, 4]
plt.scatter(a, b)         # scatter plot
```

### Data from a dataframe + labeling a chart

```python
x = df['column_1']
y = df['column_2']

plt.bar(x, y)                            # chart from dataframe data
plt.ylabel('y axis value')                # y axis label
plt.title('Chart title!')                  # chart title
plt.legend()                                # shows the legend
```

### Formatting and layout

```python
df['color'] = 'C0'                                              # color for all rows
ax.grid(True, axis='x', linestyle='--', alpha=0.7)                # grid on the x axis
ax.tick_params(left=False, bottom=False)                            # turns off ticks
plt.tight_layout()                                                    # elements don't overlap
format_axes()                                                           # formats the axes

plt.xlim(1960, 1990)   # limits the data range to the given values

fig.savefig('name')   # saves the chart under the given name
fig.show()               # displays the chart
```

### Models (regression)

```python
LinearModel()       # creates a linear chart model
QuadraticModel()      # creates a quadratic chart model (y = x^2 + 3b + 1)
```

### Changing color, line style, and markers

```python
plt.plot(x, y, 'r--o')
# 'r'  = red color
# '--' = dashed line
# 'o'  = circle-shaped marker
plt.title('Chart with red dashed lines and circles')
plt.show()
```

### Multi-panel charts (subplots)

```python
plt.figure(figsize=(10, 4))   # figure size (width, height)

plt.subplot(1, 2, 1)   # 1 row, 2 columns, first chart
plt.plot(x, y)
plt.title('Chart 1')

plt.subplot(1, 2, 2)   # 1 row, 2 columns, second chart
plt.bar(x, y)
plt.title('Chart 2')

plt.tight_layout()   # so the charts don't overlap
plt.show()
```

### Logarithmic Y axis scale

```python
plt.plot(x, y)
plt.yscale('log')   # switches the Y axis to logarithmic
plt.title('Chart with a logarithmic Y axis')
plt.show()
```

### Rotating X axis labels

Useful when labels are long and overlap:

```python
plt.bar(x, y)
plt.xticks(rotation=45)   # rotates the X axis labels by 45 degrees
plt.show()
```

### Changing chart size

```python
plt.figure(figsize=(8, 6))   # chart size: 8 inches wide, 6 inches tall
plt.plot(x, y)
plt.show()
```

## 2. Seaborn - nicer charts

```python
import seaborn as sns
import matplotlib.pyplot as plt   # seaborn is built on matplotlib, so this is needed too
```

### Basic functions

```python
sns.barplot(x, y, data=...)        # bar chart with automatic aggregation (mean, deviation)
sns.scatterplot(x, y, data=...)     # scatter plot
sns.lineplot(x, y, data=...)          # line plot
sns.histplot(data, x=..., bins=...)     # histogram
sns.boxplot(x, y, data=...)               # box plot (distribution analysis, outlier detection)
sns.heatmap(data)                           # heatmap (e.g. correlations)
```

### Examples

```python
# Bar chart
sns.barplot(x='column_1', y='column_2', data=df)
plt.title('Seaborn bar chart')
plt.show()

# Scatter plot colored by category
sns.scatterplot(x='age', y='income', hue='gender', data=df)
plt.title('Income by age and gender')
plt.show()
```
