#This script is for finding from a specific key-shop, i-e the example of Kinguin is done in this script, modify according to your needs.
#The major part of why this is a different file is for the post request that needs to be done for a shop hidden under load more.
#You need to put into your env file 2 values, csrf and cookie. 
#You can get csrf from payload tab, after you open Network inspector in the dev tools, clicking on Load More option.
#Then, click the XHR, there will be the payload tab.
#The cookie, is under the same XHR, in the Headers Tab, under Request Headers.
#I matched the headers to be the same as done in the XHR post request, which is what lead to the script working otherwise it wouldn't.


########## 2 Soups are created, I know which greatly slows the script down, but the first soup finds the gameID, which is impossible to find otherwise.#########
########## the later part of getting data for a specific keyshop is done using the post request utilizing that gameID so it is necessary ###########


import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import html
import lxml
import re 
from currency_converter import CurrencyConverter

load_dotenv()

print("Kinguin prices are calculated without any voucher and fees added. Look into list[0] and list[2] for those. ")
print("Lowest overall is considered with vouchers, any fees. The top one shown for keyshops on gg.deals page. \n")

gg_csrf_token = os.getenv("csrf")

gameName = input("Enter the game name: ")

#basic concatenation for url 

gameNameLower = gameName.lower()

gameNameLower = gameNameLower.replace("'s"," s ")

splitted = gameNameLower.split()
listLength = len(splitted)

for i in range(listLength):
    if(listLength == 1):
        break
    if(i==0):
        splitted.insert(i+1,'-')
    elif (i>1):
        splitted.insert(i*2 - 1,'-')
    i=i+1

updatedListLength = len(splitted)
gameNameWithDashes = ''.join(splitted)

url = "https://gg.deals/game/" + gameNameWithDashes

#creating response and soup

response = requests.get(url)

soup = BeautifulSoup(response.text, 'lxml')

lowestPrice = ''

#find the major keyshops lowest price shown on top, get the first one and break

for data in soup.findAll('span',{'class':'price-inner numeric'}):
    if('~' in data.text):
        lowestPrice = data.text
        lowestPrice = lowestPrice.replace('~','')
        break

#finding gameID for post request, (POST for the load more option, to get to kinguin if it is hidden below load more options)

divs = soup.findAll('div')

gameID = 0

for div in divs:
    gameID = div.get('data-container-game-id')
    if (gameID is None):
        continue;   
    intID = int(gameID)             
    if (intID > 0):
        gameID = intID
        break

url = f"https://gg.deals/us/games/keyshopsDeals/{gameID}/"

#creating header for new request

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    "Referer": f"https://gg.deals/game/" + gameName,  
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest", 
}

#from payload

data = {
    "gg_csrf": gg_csrf_token  
}

cookies = {
    "cookie": os.getenv("cookie")
}

#posting

response = requests.post(url, headers=headers, data=data, cookies=cookies)

if response.status_code != 200:
    print(f"Failed. Status code: {response.status_code}, Response: {response.text}")

#soup 

soup = BeautifulSoup(response.text, 'html.parser')

#kinguin div

list_ = []

kinguin_shop = soup.find('div', {'data-shop-name': 'Kinguin'})

kinguin_shop_str = str(kinguin_shop)

kinguin_shop_str = kinguin_shop_str.replace('&lt;','<')
kinguin_shop_str = kinguin_shop_str.replace('&gt;','>')

with open('a.txt','w') as f:
        print(kinguin_shop, file=f)

#pull-right finds the 3 values, w/ voucher, w/o, w/ voucher & fee

span_values = re.findall(r'<span class="pull-right">(.*?)</span>', kinguin_shop_str)

for data in span_values:
        list_.append(data)

#list gets all 3 values, in list[0],[1],[2]

list_.sort()

c = CurrencyConverter()
kinguinPriceFormatted = list_[1].replace('$','')

kinguinPrice = float(kinguinPriceFormatted)

#0.35 eur fixed fee to usd

fixed35fee = c.convert(0.35, 'EUR', 'USD')
kinguinPrice = kinguinPrice - fixed35fee
kinguinPrice = kinguinPrice - (kinguinPrice * 0.14)         # iwtr = base price - 0.35 eur        # iwtr = iwtr - (14% of iwtr)

iwtrFinal = format(kinguinPrice , '.2f') # CHANGES FLOAT NUMBER TO STRING AUTOMATICALLY, AND ROUNDING OFF by 2 DECIMAL PLACES
iwtrFinal = '$' + iwtrFinal

print(gameName + ":")
print("Lowest overall: " + lowestPrice)
print("Lowest on Kinguin: " + list_[1])
print("IWTR: " + iwtrFinal + "\n")        