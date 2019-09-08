from textblob import TextBlob
from textblob.np_extractors import ConllExtractor
from textblob.taggers import NLTKTagger
from textblob import Word
import wikipediaapi


nltk_tagger = NLTKTagger()
good_PoS_Tags = ["NN", "NNS", "NNP", "NNPS"]
wiki_wiki = wikipediaapi.Wikipedia('en')

def wikicategories(category):
    page_py = wiki_wiki.page(category)
    if len(category) > 2 and page_py.exists() and ("refer to:" != page_py.summary[-9:]):
        return page_py.title
    return ""

def getShingles(target_tweet):

    entityDict = {}

    blob = TextBlob(target_tweet, pos_tagger=nltk_tagger)

    try:
        keywords = blob.pos_tags
        lastNoun = ""

        for taggedTuple in keywords:

            keyword = taggedTuple[0]
            tag = taggedTuple[1]

            if tag in good_PoS_Tags:

                wikiTitle = wikicategories(keyword.lower())
                # check if wiki article exists for entity
                if wikiTitle and keyword.lower() != "gift":

                    if keyword.lower() in entityDict:
                        entityDict[wikiTitle.lower()] += blob.sentiment.polarity
                    else:
                        entityDict[wikiTitle.lower()] = blob.sentiment.polarity

                if(lastNoun):

                    keyword = lastNoun + " " + keyword
                    wikiTitle = wikicategories(keyword.lower())
                    print(keyword)
                    if wikiTitle and keyword.lower() != "gift":

                        if keyword.lower() in entityDict:
                            entityDict[wikiTitle.lower()] += blob.sentiment.polarity
                        else:
                            entityDict[wikiTitle.lower()] = blob.sentiment.polarity

                lastNoun = keyword;

            else:
                lastNoun = ""

    except Exception as e:
        print(e)

    print(entityDict)