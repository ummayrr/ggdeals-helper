import requests
from bs4 import BeautifulSoup
import lxml
import os
from googlesearch import search
import time

query = input("Enter bundle's name: ")
query += "site: gg.deals"

result = search(query, 1) ### 1 = number of results

url = ''

for i in result:
    print(i)
    url = i

response = requests.get(url)

soup = BeautifulSoup(response.text, 'lxml')

for data in soup.findAll('div',{'class':'news-heading-title'}):
    print (data.text)
    
divs = soup.findAll('a',{'class':'game-info-title title'})
names = []

for div in divs:
   names.append(div.text)

names = list(set(names))

if(os.path.isfile('names.txt')):
    os.remove('names.txt')

for name in names:
    with open('names.txt','a') as f:
        print(name, file = f)