import operator

from PIL import Image
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from ebaysdk import finding
import urllib
import PIL;
def getProducts(categoricalEntityList,namedEntityList):

    api = Finding(appid="KerwinSu-Dena-PRD-344818667-e4b5e25e", config_file='myebay.yaml')
    print(api.execute('findItemsAdvanced', {'keywords': 'test'}).dict())

    categoricalTop3 = categoricalEntityList[:3]
    namedTop3 = namedEntityList[:3]
    categoricalScoreList = {}
    namedScoreList = {}
    combinedEntityDict = {}
    singleEntityDict = []
    api = Finding(appid="KerwinSu-Dena-PRD-344818667-e4b5e25e", config_file='myebay.yaml', )

    for categoricalEntity in categoricalTop3:
        categoricalResponse = api.execute('findItemsAdvanced',{'keywords': categoricalEntity[0], 'outputSelector': "PictureURLLarge"})
        categoricalSearchSize = int(categoricalResponse.dict()['paginationOutput']['totalEntries'])
        categoricalScoreList[categoricalEntity[0]] = categoricalSearchSize
        if (categoricalSearchSize > 100):
            try:
                singleEntityDict.append([[""],[0,categoricalResponse.dict()["searchResult"]["item"][0]["title"],
                                     str(categoricalResponse.dict()["searchResult"]["item"][0]["pictureURLLarge"])]])
            except:
                singleEntityDict.append([[""],[0, categoricalResponse.dict()["searchResult"]["item"][0]["title"],
                                     str(categoricalResponse.dict()["searchResult"]["item"][0]["galleryURL"])]])

    for namedEntity in namedTop3:
        namedResponse = api.execute('findItemsAdvanced', {'keywords': namedEntity[0],'outputSelector':"PictureURLLarge"})
        namedSearchSize = int(namedResponse.dict()['paginationOutput']['totalEntries'])
        namedScoreList[namedEntity[0]] = namedSearchSize
        if(namedSearchSize > 100):
            try:
                singleEntityDict.append([[""],[0, namedResponse.dict()["searchResult"]["item"][0]["title"],
                                         str(namedResponse.dict()["searchResult"]["item"][0]["pictureURLLarge"])]])
            except:
                singleEntityDict.append([[""],[0, namedResponse.dict()["searchResult"]["item"][0]["title"],
                                         str(namedResponse.dict()["searchResult"]["item"][0]["galleryURL"])]])

    for categoricalEntity in categoricalTop3:
        for namedEntity in namedTop3:
            try:
                if categoricalEntity[0] not in namedEntity[0]:
                    combinedResponse = api.execute('findItemsAdvanced', {'keywords': namedEntity[0] + " " + categoricalEntity[0],'outputSelector':"PictureURLLarge"})
                    combinedSearchSize = int(combinedResponse.dict()['paginationOutput']['totalEntries'])
                    namedSearchSize = namedScoreList[namedEntity[0]]
                    categoricalSearchSize = categoricalScoreList[categoricalEntity[0]]

                    if(namedSearchSize > 100 and categoricalSearchSize > 100 and combinedSearchSize > 1):
                        searchScore = combinedSearchSize/min(namedSearchSize,categoricalSearchSize)

                        print('Finding Results for: ' + namedEntity[0] + ' ' + categoricalEntity[0])
                        print('search size for ' + namedEntity[0] + '-' + str(namedSearchSize))
                        print('search size for ' + categoricalEntity[0] + '-' + str(categoricalSearchSize))

                        print('search size for ' + namedEntity[0] + ' ' + categoricalEntity[0] +
                              '-' + str(combinedSearchSize))

                        print('combined reduction value: ' + str(searchScore))
                        print('------------------------------------------------------------------')
                        try:
                            combinedEntityDict[namedEntity[0] + " " + categoricalEntity[0]] = [searchScore,combinedResponse.dict()["searchResult"]["item"][0]["title"],
                                                                                           str(combinedResponse.dict()["searchResult"]["item"][0]["pictureURLLarge"])]
                        except:
                            combinedEntityDict[namedEntity[0] + " " + categoricalEntity[0]] = [searchScore, combinedResponse.dict()["searchResult"]["item"][0]["title"],
                                                                                           str(combinedResponse.dict()["searchResult"]["item"][0]["galleryURL"])]
            except ConnectionError as e:
                print(e)
                print(e.response.dict())
    sorted_combinedEntityDict = sorted(combinedEntityDict.items(), key=operator.itemgetter(1), reverse=True)
    finalList = sorted_combinedEntityDict + singleEntityDict
    titleList = []
    print(finalList)
    i = 1
    for item in finalList:
        titleList.append( "(" + str(i) + ") " + item[1][1])
        imageUrl = str(item[1][2])
        urllib.request.urlretrieve(imageUrl,
                                   "assets/B_Item" + str(i) + ".jpg")
        im1 = Image.open("assets/B_Item" + str(i) + ".jpg")
        im_small = im1.resize((200, 200), Image.ANTIALIAS)
        im_small.save("assets/B_Item" + str(i) + ".png")
        i = i + 1
    return titleList

def getProductsForRecommender(categoricalEntityList):
    recItems = []
    for i in range(len(categoricalEntityList)):
        try:
            print(categoricalEntityList[i])
            api = Finding(appid="KerwinSu-Dena-PRD-344818667-e4b5e25e", config_file='myebay.yaml')
            namedResponse = api.execute('findItemsAdvanced', {'keywords': categoricalEntityList[i],'outputSelector':"PictureURLLarge"})
            result=namedResponse.dict()
            print(result["searchResult"]["item"][0]["title"]);
            recItems.append(result["searchResult"]["item"][0]["title"])
            try:
                imageUrl = str(result["searchResult"]["item"][0]["pictureURLLarge"])
                urllib.request.urlretrieve(imageUrl,
                                   "assets/Item"+str(i)+".jpg")
                im1 = Image.open("assets/Item"+str(i)+".jpg")
                im_small = im1.resize((100, 100), Image.ANTIALIAS)
                im_small.save("assets/Item"+str(i)+".png")
            except:
                imageUrl = str(result["searchResult"]["item"][0]["galleryURL"])
                urllib.request.urlretrieve(imageUrl,
                                           "assets/Item" + str(i) + ".jpg")
                im1 = Image.open("assets/Item" + str(i) + ".jpg")
                im_small = im1.resize((100, 100), Image.ANTIALIAS)
                im_small.save("assets/Item" + str(i) + ".png")
        except ConnectionError as e:
            print(e)
            print(e.response.dict())
    return recItems



