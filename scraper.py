from bs4 import BeautifulSoup
import requests
import lxml
import os
import roman
from googlesearch import search

globalName = ''

def basicFormatting (gameName):
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

def formatName (gameName):
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

def test5(gameName):                             ### search on google, make request is inside, returns response
    query = gameName + " site: gg.deals"
    try:
        result = search(query, 1)
        for i in result:
            response = requests.get(i, timeout=10)
            return response
    except Exception as e:
        print(f"Exception occured while searching on Google: {e}")
        return

def test6(gameName):                             ### gg.deals native search
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

def makeSoup(response,inputNameForDisplay):
    soup = BeautifulSoup(response.text, 'lxml')

    for data in soup.findAll('a',{'class':'game-info-title title no-icons'}):
     global globalName
     globalName = data.text
     break

    for data in soup.findAll('span',{'class':'price-inner numeric'}):
        if('~' in data.text):
            lowest = data.text
            lowest = lowest.replace('~','')
            print(globalName + ": " + lowest)
            with open('results.txt','a') as f:
                print(globalName + ": " + lowest, file = f)
            break
        
def driver(inputName):
    inputNameForDisplay = inputName
    inputName = basicFormatting (inputName)
    inputNameFormatted = formatName(inputName)
    #create request to the URL 
    
    response = makeRequest(inputNameFormatted)
    
    if (response.status_code == 404 and "'s" in inputName):
        response = makeRequest(test1(inputName))
        if (response.status_code == 404):
            response = makeRequest(test2(inputName))
            
    test3Result = test3(inputName)
    if(response.status_code == 404 and test3Result != ''):
        response = makeRequest(test3Result)
    
    test4Result = test4(inputName)
    if (response.status_code == 404 and test4Result != ''):
        response = makeRequest(test4Result)
    
    if not response or response.status_code == 404:
        try:
         response = test5(inputNameForDisplay)
        except:
            response = test6(inputNameForDisplay)

    if not response or response.status_code == 404:
            print("All tries to search for the game have failed. ")
            return
    
    makeSoup(response,inputNameForDisplay)

if(os.path.isfile('results.txt')):
 os.remove('results.txt')

with open('names.txt','r') as f:
    try:
        for line in f:
                    driver(line.rstrip())
    except Exception as e:
         print(f"Exception occured: {e}")
        