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
import roman
from currency_converter import CurrencyConverter
from googlesearch import search

load_dotenv()

print("Kinguin prices are calculated without any voucher and fees added. Look into list[0] and list[2] for those. ")
print("Lowest overall is considered with vouchers, any fees. The top one shown for keyshops on gg.deals page. \n")

gg_csrf_token = os.getenv("csrf")
gameName = ''
iwtrTotal = 0.0
globalName = ''

def basicFormatting (gameName):                          ### basic symbols removal
    gameName = gameName.replace(':','')
    gameName = gameName.replace('-','')
    gameName = gameName.replace(',','')
    gameName = gameName.replace('+','')
    gameName = gameName.replace('(','')
    gameName = gameName.replace(')','')
    gameName = gameName.replace('!','')
    gameName = gameName.replace('.','')
    gameName = gameName.replace('®','')
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

def test1(gameName):                            ### Assassins' Creed to Assassins Creed
    gameName = gameName.replace("'","")
    gameName = formatName(gameName)
    return gameName

def test2(gameName):                            ### Assassin's Creed to Assassin-s-Creed
    gameName = gameName.replace("'s"," s ")
    gameName = formatName(gameName)
    return gameName

def test3(gameName):                            ### Assassin's Creed to Assassins Creed
    gameName = gameName.replace("'s","s")
    gameName = formatName(gameName)
    return gameName

def test4(gameName):                            ### The Darkness II to The Darkness 2
    gameNameList = gameName.split()
    testStr = "Hello"

    index = 0

    for i in range(len(gameNameList)):
        testStr = gameNameList[i]
        if (
            ((testStr[0] == 'I' or testStr[0] == 'i') and (testStr[-1] == 'I' or testStr[-1] == 'i')) or
            ((testStr[0] == 'I' or testStr[0] == 'i') and (testStr[-1] == 'X' or testStr[-1] == 'x')) or
            (testStr.lower() == 'x') or
            (testStr[0] == 'I' or testStr[0] == 'i') or
            (testStr[-1] == 'V' or testStr[-1] == 'v') or
            ((testStr[0] == 'X' or testStr[0] == 'x') and (testStr[-1] == 'V' or testStr[-1] == 'v')) or
            ((testStr[0] == 'X' or testStr[0] == 'x') and (testStr[-1] == 'I' or testStr[-1] == 'i'))
        ):
            index = i
            break


    count = 0

    if index == 0:
        return ''

    number = int(roman.fromRoman(gameNameList[index].upper()))

    gameNameList[index] = str(number)

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

def test5(gameName):                            ### Dark Souls 3 to Dark Souls III
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
        return ''

    romanStr = ""

    romanStr = str(roman.toRoman(testInt))

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

def test6(gameName):                             ### search on google, make request is inside, returns response
    query = gameName + " site: gg.deals"
    try:
        result = search(query, 1)
        for i in result:
            response = requests.get(i, timeout=10)
            return response
    except Exception as e:
        print(f"Exception occured while searching on Google: {e}")
        return

def test7(gameName):                             ### gg.deals native search
    url = "https://gg.deals/search/?title=" + gameName
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')

    divs = soup.findAll('div')

    for div in divs:
      linkName = div.get('data-game-name')
      if (linkName is None):
       continue;   
      break

    url = "https://gg.deals/game/" + linkName

    response = requests.get(url, timeout=10)
    return response
    
def makeRequest (gameName):
       url = "https://gg.deals/game/" + gameName
#      print(url)
       response = requests.get(url,timeout=10)
       return response


def initialSoup (response):                      #required for getting gameID mainly, is also finding game name for displaying
    soup = BeautifulSoup(response.text, 'lxml')
    
    for value in soup.findAll('a',{'class':'active'}):
       tempName = value.text
       break
 
    tempName = os.linesep.join([s for s in tempName.splitlines() if s])
    global globalName
    globalName = tempName
 
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


def kinguinExtractor(soup1, soup2):                  ### soup 1 is only passed to pass into final function
    
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
    
    global iwtrTotal
    iwtrTotal += kinguinPrice
    iwtrFinal = format(kinguinPrice , '.2f') # CHANGES FLOAT NUMBER TO STRING AUTOMATICALLY, AND ROUNDING OFF by 2 DECIMAL PLACES
    iwtrFinal = '$' + iwtrFinal
    lowestOnKinguin = list_[1]
    final(soup1, lowestOnKinguin, iwtrFinal)
         
def printer(lowestPrice, lowestOnKinguin, iwtrFinal):          ## printing all output
    with open('results.txt','a') as f:
        #### print to file ####
     print(globalName + ":", file = f)
     print("Lowest overall: " + lowestPrice, file = f)
     print("Lowest on Kinguin: " + lowestOnKinguin, file = f)
     print("IWTR: " + iwtrFinal + "\n", file = f)  
        #### print to console #### 
     print(globalName + ":")
     print("Lowest overall: " + lowestPrice)
     print("Lowest on Kinguin: " + lowestOnKinguin)
     print("IWTR: " + iwtrFinal + "\n")  

def final(soup1, lowestOnKinguin, iwtrFinal):      ## finds lowest price overall, and passes to print function everything
    lowestPrice = ''
    result = soup1.findAll('span',{'class':'price-inner numeric'})[1].text

    if('~' in result):
            lowestPrice = result
            lowestPrice = lowestPrice.replace('~','')
    else:
        lowestPrice = result    
     
    printer(lowestPrice, lowestOnKinguin, iwtrFinal)    

def driver(inputName):                                             ### main driver
    inputNameForDisplay = inputName
    inputName = basicFormatting (inputName)
    inputNameFormatted = formatName(inputName)
    
    #create request to the URL 
    
    response = makeRequest(inputNameFormatted)
    
    if (response.status_code == 404 and "'" in inputName):
        response = makeRequest(test1(inputName))
    
    if (response.status_code == 404 and "'s" in inputName):
            response = makeRequest(test2(inputName))
            if (response.status_code == 404):
                response = makeRequest(test3(inputName))
            
    test4Result = test4(inputName)
    if(response.status_code == 404 and test4Result != ''):
        response = makeRequest(test4Result)
    
    test5Result = test5(inputName)
    if (response.status_code == 404 and test5Result != ''):
        response = makeRequest(test5Result)
    
    if not response or response.status_code == 404:
        try:
         response = test6(inputNameForDisplay)
        except:
            response = test7(inputNameForDisplay)
            
    if not response or response.status_code == 404:
            print("All tries to search for the game have failed. ")
            return
    
    soup1 = initialSoup(response)
    secondSoup = findGameID(soup1)
    kinguinExtractor(soup1, secondSoup)
    
     ### actual main ###

if(os.path.isfile('results.txt')):
 os.remove('results.txt')

with open('names.txt','r') as f:
   for line in f:
       try:
            driver(line.rstrip())
       except IndexError:
            with open('results.txt','a') as f:
             print(f"Could not find a listing for {line.rstrip()} on Kinguin.\n")
             print(f"Could not find a listing for {line.rstrip()} on Kinguin.\n", file = f)
       except Exception as e:
            print(f"Exception occured: {e}")
            
iwtrFinalStr = format(iwtrTotal , '.2f') # CHANGES FLOAT NUMBER TO STRING AUTOMATICALLY, AND ROUNDING OFF by 2 DECIMAL PLACES
iwtrFinalStr = '$' + iwtrFinalStr
print("IWTR Total: " + iwtrFinalStr)

with open('results.txt','a') as f:
    print("IWTR Total: " + iwtrFinalStr, file = f)