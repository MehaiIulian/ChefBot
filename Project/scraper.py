from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "https://en.wikibooks.org/wiki/Cookbook:Ingredients"

# We use try-except incase the request was unsuccessful because of
# wrong URL
try:
   page = urlopen(url)
except:
   print("Error opening the URL")

soup = BeautifulSoup(page, 'html.parser')

content = soup.find('div', {"id": "mw-content-text"})

article = ''
for i in content.findAll('li'):
    article = article + ' ' +  i.text

with open('scraped_text.txt', 'w') as file:
    file.write(article)

print(article)