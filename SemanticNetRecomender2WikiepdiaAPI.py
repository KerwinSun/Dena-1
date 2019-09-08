import re
import tweepy
import csv
import spacy
from TaxonomySearcher import TaxonomySearcher
from textblob import TextBlob
from textblob.np_extractors import ConllExtractor
from textblob.taggers import NLTKTagger
from textblob import Word
import string
import wikipediaapi
import operator
import EbayProductFinding

wiki_wiki = wikipediaapi.Wikipedia('en')
consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
access_token_secret ="RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

extractor = ConllExtractor()
nltk_tagger = NLTKTagger()
searcher = TaxonomySearcher()
npl = spacy.load("en_core_web_lg")

good_labels = ["PERSON", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK OF ART", "LANGUAGE"]
good_PoS_Tags = ["NN", "NNS", "NNP", "NNPS"]

file = open('TaxonomyUserTarget.csv', 'a', newline='', encoding="utf-8")
writer = csv.writer(file)

# helper methods to assist in sanitising tweets before analysis
def clean(inputString):
    inputString = re.sub(r"http\S+", "", inputString)
    inputString = re.sub(r"@\S+", "", inputString)
    printable = set(string.printable)
    filter(lambda x: x in printable, inputString)
    return inputString.encode('ascii', 'ignore').decode('ascii')

def wikicategories(category):
    page_py = wiki_wiki.page(category)
    if len(category) > 2 and page_py.exists() and ("refer to:" != page_py.summary[-9:]):
        return page_py.title
    return ""
'''
def wikicategories(category):
    page_py = wiki_wiki.page(category)
    if len(category) > 2 and page_py.exists() and ("refer to:" != page_py.summary[-9:]):
        return True
    return False
'''
def doTextAnalysis(text):
    entityDict = {}
    NamedEntityDict = {}
    CategoricalEntityDict = {}
    text = clean(text)
    blob = TextBlob(text, pos_tagger=nltk_tagger)

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
                    #print(wikiTitle)
                    if keyword.lower() in entityDict:
                        entityDict[wikiTitle.lower()] += blob.sentiment.polarity
                    else:
                        entityDict[wikiTitle.lower()] = blob.sentiment.polarity

                if (lastNoun):

                    keyword = lastNoun + " " + keyword
                    wikiTitle = wikicategories(keyword.lower())
                    if wikiTitle and keyword.lower() != "gift":
                        #print(wikiTitle)
                        if keyword.lower() in entityDict:
                            entityDict[wikiTitle.lower()] += blob.sentiment.polarity
                        else:
                            entityDict[wikiTitle.lower()] = blob.sentiment.polarity

                lastNoun = keyword;

            else:
                lastNoun = ""

    except Exception as e:
        print(e)

    try:
        doc = npl(text)
        for entity in doc.ents:
            if entity.label_ in good_labels:
                NamedEntityDict[entity.text.lower()] = 0;

    except Exception as e:
        print(e)

    synsetDict = {}

    for entity in entityDict:

        nets = Word(entity).synsets
        if len(nets) > 0:
            net = nets[0]
            synsetDict[entity] = net
            CategoricalEntityDict[entity] = entityDict[entity]
        else:
            NamedEntityDict[entity] = entityDict[entity]
            #print(entity + " - added to named entity list")


    return [NamedEntityDict,CategoricalEntityDict]


def doUserAnalysis(user):
    user = api.get_user(user)
    print(user)
    userid = user.id

    statuses = api.user_timeline(
        #define number of tweets to pick from

        user_id=userid, include_rts=False, exclude_replies=True, tweet_mode="extended", count = 20)

    entityDict = {}
    NamedEntityDict = {}
    CategoricalEntityDict = {}

    for status in statuses:

        print(status)
        target_tweet = clean(status.full_text)

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
                        print(wikiTitle)
                        if keyword.lower() in entityDict:
                            entityDict[wikiTitle.lower()] += blob.sentiment.polarity
                        else:
                            entityDict[wikiTitle.lower()] = blob.sentiment.polarity

                    if (lastNoun):

                        keyword = lastNoun + " " + keyword
                        wikiTitle = wikicategories(keyword.lower())
                        if wikiTitle and keyword.lower() != "gift":
                            print(wikiTitle)
                            if keyword.lower() in entityDict:
                                entityDict[wikiTitle.lower()] += blob.sentiment.polarity
                            else:
                                entityDict[wikiTitle.lower()] = blob.sentiment.polarity

                    lastNoun = keyword;

                else:
                    lastNoun = ""

        except Exception as e:
            print(e)


        # get named nouns
        try:
            doc = npl(target_tweet)
            for entity in doc.ents:
                if entity.label_ in good_labels:
                    NamedEntityDict[entity.text.lower()] = 0;

        except Exception as e:
            print(e)

    #print(entityDict)

    #TODO: algorithm for extracting multiword entites e.g "gift cards"

    ##use synnet to find similarity between words, find entity with most similarity score

    ##generate synsets for every enetity
    synsetDict = {}

    for entity in entityDict:

        nets = Word(entity).synsets
        if len(nets) > 0:
            net = nets[0]
            synsetDict[entity] = net
            CategoricalEntityDict[entity] = entityDict[entity]
        else:
            NamedEntityDict[entity] = entityDict[entity]
            print(entity + " - added to named entity list")

    print(synsetDict)

    '''
    ##calculate entity with largest synset similarity score
    synsetScoreDict = {}
    
    for synsetEntity in synsetDict:
    
        synsetScoreDict[synsetEntity] = 0;
    
        for comparativeEntity in synsetDict:
    
            if(synsetEntity != comparativeEntity):
    
                entity1 = synsetDict[synsetEntity]
                entity2 = synsetDict[comparativeEntity]
                score = entity1.path_similarity(entity2)
                if(score):
                    synsetScoreDict[synsetEntity] += score
    
    print(synsetScoreDict)
    '''
    sorted_categoricalEntityDict = sorted(CategoricalEntityDict.items(), key=operator.itemgetter(1), reverse=True)
    sorted_namedEntityDict = sorted(NamedEntityDict.items(), key=operator.itemgetter(1), reverse=True)

    return EbayProductFinding.getProducts(sorted_categoricalEntityDict, sorted_namedEntityDict)

