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
    combinedEntityDict = {}


    for categoricalEntity in categoricalTop3:

        for namedEntity in namedTop3:

            try:
                if categoricalEntity[0] not in namedEntity[0]:
                    api = Finding(appid="KerwinSu-Dena-PRD-344818667-e4b5e25e", config_file='myebay.yaml')
                    namedResponse = api.execute('findItemsAdvanced', {'keywords': namedEntity[0]})
                    categoricalResponse = api.execute('findItemsAdvanced', {'keywords': categoricalEntity[0]})
                    combinedResponse = api.execute('findItemsAdvanced', {'keywords': namedEntity[0] + " " + categoricalEntity[0]})

                    namedSearchSize = int(namedResponse.dict()['paginationOutput']['totalEntries'])
                    categoricalSearchSize = int(categoricalResponse.dict()['paginationOutput']['totalEntries'])
                    combinedSearchSize = int(combinedResponse.dict()['paginationOutput']['totalEntries'])

                    searchScore = combinedSearchSize/min(namedSearchSize,categoricalSearchSize)

                    print('Finding Results for: ' + namedEntity[0] + ' ' + categoricalEntity[0])
                    print('search size for ' + namedEntity[0] + '-' + str(namedSearchSize))
                    print('search size for ' + categoricalEntity[0] + '-' + str(categoricalSearchSize))

                    print('search size for ' + namedEntity[0] + ' ' + categoricalEntity[0] +
                          '-' + str(combinedSearchSize))

                    print('combined reduction value: ' + str(searchScore))
                    print('------------------------------------------------------------------')

                    combinedEntityDict[namedEntity[0] + " " + categoricalEntity[0]] = str(searchScore)

            except ConnectionError as e:
                print(e)
                print(e.response.dict())



def getProductsForRecommender(categoricalEntityList):
    recItems = [len(categoricalEntityList)]
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
                                   "Item"+str(i)+".jpg")
                im1 = Image.open("Item"+str(i)+".jpg")
                im_small = im1.resize((100, 100), Image.ANTIALIAS)
                im_small.save("Item"+str(i)+".png")
            except:
                imageUrl = str(result["searchResult"]["item"][0]["galleryURL"])
                urllib.request.urlretrieve(imageUrl,
                                           "Item" + str(i) + ".jpg")
                im1 = Image.open("Item" + str(i) + ".jpg")
                im_small = im1.resize((100, 100), Image.ANTIALIAS)
                im_small.save("Item" + str(i) + ".png")
        except ConnectionError as e:
            print(e)
            print(e.response.dict())
    return recItems



