from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from ebaysdk import finding

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


