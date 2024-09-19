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
gameName = ''

def basicFormatting (gameName):                          ### basic symbols removal
    gameName = gameName.replace(':','')
    gameName = gameName.replace('-','')
    gameName = gameName.replace(',','')
    gameName = gameName.replace('+','')
    gameName = gameName.replace('(','')
    gameName = gameName.replace(')','')
    gameName = gameName.replace('!','')
    gameName = gameName.replace('.','')
    return gameName

def formatName (gameName):                                 ### add dashes and convert to the main form for gg.deals/game/this-form-here from name sent in spaces
    gameNameLower = gameName.lower()
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
    return gameNameWithDashes

def test1(gameName):                            ### Assassin's Creed to Assassin-s-Creed
    gameName = gameName.replace("'s"," s ")
    gameName = formatName(gameName)
    return gameName

def test2(gameName):                            ### Assassin's Creed to Assassins Creed
    gameName = gameName.replace("'s","s")
    gameName = formatName(gameName)
    return gameName

def test3(gameName):                            ### The Darkness II to The Darkness 2
    gameNameList = gameName.split()
    testStr = "Hello"

    index = 0

    for i in range(len(gameNameList)):
        testStr = gameNameList[i]
        if ((testStr[0] == 'I' or testStr[0] == 'i') and (testStr[-1] == 'I' or testStr[-1] == 'i')):
            index = i
            break

    count = 0

    if index == 0:
        return gameName


    for i in testStr:
        count = count + 1

    gameNameList[index] = str(count)

    for i in range(len(gameNameList)):
     if(len(gameNameList) == 1):
        break
     if(i==0):
        gameNameList.insert(i+1,' ')
     elif (i>1):
        gameNameList.insert(i*2 - 1,' ')
     i=i+1

    gameName = ''.join(gameNameList)
    gameName = formatName(gameName)
    return gameName

def test4(gameName):                            ### Dark Souls 3 to Dark Souls III
    gameNameList = gameName.split()

    testInt = 0
    index = 0

    for i in range(len(gameNameList)):
        test = gameNameList[i]
        try:
            testInt = int(test)
            if (testInt > 0):
             index = i
             break
        except:
            continue
        i+=1

    if (testInt == 0):
        return gameName

    romanStr = ""

    for i in range(testInt):
        romanStr += 'I'

    gameNameList[index] = romanStr

    for i in range(len(gameNameList)):
     if(len(gameNameList) == 1):
       break
     if(i==0):
       gameNameList.insert(i+1,' ')
     elif (i>1):
       gameNameList.insert(i*2 - 1,' ')
    i=i+1

    gameName = ''.join(gameNameList)
    gameName = formatName (gameName)
    return gameName

def makeRequest (gameName):
    url = "https://gg.deals/game/" + gameName
    print(url)
    response = requests.get(url)
    return response

def initialSoup (response):                      #required for getting gameID mainly
    soup = BeautifulSoup(response.text, 'lxml')
    return soup

def findGameID (soup1):                        #finding gameID for post request, (POST for the load more option, to get to kinguin if it is hidden below load more options)
    divs = soup1.findAll('div')

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
        
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def kinguinExtractor(soup1, soup2, inputNameForDisplay):                  ### soup 1 is only passed to pass into final function

    
    #kinguin div

    list_ = []

    kinguin_shop = soup2.find('div', {'data-shop-name': 'Kinguin'})

    kinguin_shop_str = str(kinguin_shop)

    kinguin_shop_str = kinguin_shop_str.replace('&lt;','<')
    kinguin_shop_str = kinguin_shop_str.replace('&gt;','>')

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
    lowestOnKinguin = list_[1]
    final(soup1, inputNameForDisplay, lowestOnKinguin, iwtrFinal)
         
def printer(inputNameForDisplay, lowestPrice, lowestOnKinguin, iwtrFinal):          ## printing all output
    with open('results.txt','a') as f:
     print(inputNameForDisplay + ":", file = f)
     print("Lowest overall: " + lowestPrice, file = f)
     print("Lowest on Kinguin: " + lowestOnKinguin, file = f)
     print("IWTR: " + iwtrFinal + "\n", file = f)   

def final(soup1, inputNameForDisplay, lowestOnKinguin, iwtrFinal):      ## finds lowest price overall, and passes to print function everything
    lowestPrice = ''

    for data in soup1.findAll('span',{'class':'price-inner numeric'}):
        if('~' in data.text):
            lowestPrice = data.text
            lowestPrice = lowestPrice.replace('~','')
            break
     
    printer(inputNameForDisplay, lowestPrice, lowestOnKinguin, iwtrFinal)    

def driver(inputName):                                             ### main driver
    inputNameForDisplay = inputName
    inputName = basicFormatting (inputName)
    #create request to the URL 
    response = makeRequest(test1(inputName))
    if (response.status_code == 404):
          response = makeRequest(test2(inputName))
          if (response.status_code == 404):
           response = makeRequest(test3(inputName))
           if (response.status_code == 404):
            response = makeRequest(test4(inputName))
    
    soup1 = initialSoup(response)
    secondSoup = findGameID(soup1)
    kinguinExtractor(soup1, secondSoup, inputNameForDisplay)
    
     ### actual main ###

if(os.path.isfile('results.txt')):
 os.remove('results.txt')

with open('names.txt','r') as f:
  for line in f:
    driver(line.rstrip())