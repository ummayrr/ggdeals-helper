import traceback
from bs4 import BeautifulSoup
import requests
import lxml
import os
import roman
import re
from googlesearch import search

globalName = ''

def basicFormatting(gameName):
    gameName = gameName.replace(':', '')
    gameName = gameName.replace('-', '')
    gameName = gameName.replace(',', '')
    gameName = gameName.replace('+', '')
    gameName = gameName.replace('(', '')
    gameName = gameName.replace(')', '')
    gameName = gameName.replace('!', '')
    gameName = gameName.replace('.', '')
    gameName = gameName.replace('®', '')
    return gameName

def formatName(gameName):
    gameNameLower = gameName.lower()
    splitted = gameNameLower.split()
    listLength = len(splitted)

    for i in range(listLength):
        if listLength == 1:
            break
        if i == 0:
            splitted.insert(i+1, '-')
        elif i > 1:
            splitted.insert(i*2 - 1, '-')
        i = i + 1

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
        testStr = testStr.lower() 
        
        validRomans = [
          'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 
          'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 
          'xvi', 'xvii', 'xviii', 'xix', 'xx','xxi','xxii','xxiii','xxiv','xxv','xxvi','xxvii','xxviii','xxix','xxx']
        
        if testStr in validRomans:
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


def makeRequest(gameName):
    try:
        url = f"https://gg.deals/game/{gameName}"
        response = requests.get(url, timeout=10)
        return response
    except Exception as e:
        print(f"Exception occurred in makeRequest: {e}")
        return None

def makeSoup(response, inputNameForDisplay):
    try:
        soup = BeautifulSoup(response.text, 'lxml')

        for value in soup.findAll('a', {'class': 'active'}):
            tempName = value.text
            break

        tempName = os.linesep.join([s for s in tempName.splitlines() if s])
        global globalName
        globalName = tempName

        result = soup.findAll('span', {'class': 'price-inner numeric'})[1].text

        if '~' in result:
            lowest = result.replace('~', '')
        else:
            lowest = result

        print(f"{globalName}: {lowest}")

        with open('results.txt', 'a') as f:
            print(f"{globalName}: {lowest}", file=f)

    except Exception as e:
        print(f"Exception in makeSoup: {e}")
        return

def driver(inputName):
    try:
        inputNameForDisplay = inputName
        inputName = basicFormatting(inputName)
        inputNameFormatted = formatName(inputName)

        response = makeRequest(inputNameFormatted)

        if response and response.status_code == 404 and "'" in inputName:
            response = makeRequest(test1(inputName))

        if response and response.status_code == 404 and "'s" in inputName:
            response = makeRequest(test2(inputName))
            if response and response.status_code == 404:
                response = makeRequest(test3(inputName))

        test4Result = test4(inputName)
        if response and response.status_code == 404 and test4Result != '':
            response = makeRequest(test4Result)

        test5Result = test5(inputName)
        if response and response.status_code == 404 and test5Result != '':
            response = makeRequest(test5Result)

        if not response or response.status_code == 404:
            try:
                response = test6(inputNameForDisplay)
            except:
                response = test7(inputNameForDisplay)

        if not response or response.status_code == 404:
            print(f"All tries failed for game: {inputNameForDisplay}")
            return

        makeSoup(response, inputNameForDisplay)

    except Exception as e:
        print(f"Exception in driver for {inputNameForDisplay}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    if os.path.isfile('results.txt'):
        os.remove('results.txt')

    with open('names.txt', 'r') as f:
        for line in f:
            try:
                game_name = line.rstrip()
                driver(game_name)
            except Exception as e:
                print(f"Exception occurred while processing {game_name}: {e}")
                traceback.print_exc()