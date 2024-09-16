from bs4 import BeautifulSoup
import requests
import lxml

gameName = input("Enter the game name: ")
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

print("\n")
url = "https://gg.deals/game/" + gameNameWithDashes
print (url)
print("\n")

response = requests.get(url)

soup = BeautifulSoup(response.text, 'lxml')

for data in soup.findAll('span',{'class':'price-inner numeric'}):
    if('~' in data.text):
        print(gameName + " - Lowest: " + data.text)
        break


for data in soup.findAll('span',{'class':'price-inner game-price-current'}):
    print(data.text)