from bs4 import BeautifulSoup
import requests
import lxml

gameName = input("Enter the game name: ")

#basic concatenation for game URL

gameNameLower = gameName.lower()

gameNameLower = gameNameLower.replace("'s"," s ")
gameNameLower = gameNameLower.replace(':','')
gameNameLower = gameNameLower.replace('-','')

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

#create request to the URL 

print("\n")
url = "https://gg.deals/game/" + gameNameWithDashes

response = requests.get(url)

#soup

soup = BeautifulSoup(response.text, 'lxml')

for data in soup.findAll('span',{'class':'price-inner numeric'}):
    if('~' in data.text):
        lowest = data.text
        lowest = lowest.replace('~','')
        print(gameName + ": " + lowest + "\n")
        break