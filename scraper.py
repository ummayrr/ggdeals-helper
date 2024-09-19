from bs4 import BeautifulSoup
import requests
import lxml
import os

def basicFormatting (gameName):
    gameName = gameName.replace(':','')
    gameName = gameName.replace('-','')
    gameName = gameName.replace(',','')
    gameName = gameName.replace('+','')
    gameName = gameName.replace('(','')
    gameName = gameName.replace(')','')
    gameName = gameName.replace('!','')
    gameName = gameName.replace('.','')
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
    try:
       url = "https://gg.deals/game/" + gameName
#      print(url)
       response = requests.get(url,timeout=10)
       response.raise_for_status() 
       return response
    except requests.exceptions.RequestException as e:
     print(f"Request failed: {e}")
     return None

def makeSoup(response,inputNameForDisplay):
    soup = BeautifulSoup(response.text, 'lxml')

    for data in soup.findAll('span',{'class':'price-inner numeric'}):
        if('~' in data.text):
            lowest = data.text
            lowest = lowest.replace('~','')
            print(inputNameForDisplay + ": " + lowest)
            with open('results.txt','a') as f:
                print(inputNameForDisplay + ": " + lowest, file = f)
            break

def driver(inputName):
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
            if not response or response.status_code == 404:
             print(f"Could not find the game: {inputNameForDisplay}")
             return


    #soup

    makeSoup(response,inputNameForDisplay)

if(os.path.isfile('results.txt')):
 os.remove('results.txt')
with open('names.txt','r') as f:
    for line in f:
        driver(line.rstrip())
        