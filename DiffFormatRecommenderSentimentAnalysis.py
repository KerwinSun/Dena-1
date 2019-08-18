import csv
import string
import urllib.request
import os
import tweepy
import wikipediaapi
from imageai.Detection import ObjectDetection
from ibm_watson import NaturalLanguageUnderstandingV1
from textblob import TextBlob
import spacy
from textblob.taggers import NLTKTagger
from TaxonomySearcher import TaxonomySearcher
import re
writefile = open('user-id-sentiment-category_and_score', 'a', newline='')
userwritefile = open('user-id', 'a', newline='')
itemwritefile = open('item-id', 'a', newline='')
writer = csv.writer(writefile)
userwriter = csv.writer(userwritefile)
itemwriter = csv.writer(itemwritefile)
consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
access_token_secret ="RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
wiki_wiki = wikipediaapi.Wikipedia('en')
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
tweets = tweepy.Cursor(api.search,
                       q="gift",lang="en",result_type='mixed').items(45);
execution_path = os.getcwd()
good_PoS_Tags = ["NN", "NNS", "NNP", "NNPS"]
detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath(os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
detector.loadModel()
searcher = TaxonomySearcher();
nlp = spacy.load("en_core_web_lg")
nltk_tagger = NLTKTagger()
count = 0
good_labels = ["PERSON", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK OF ART", "LANGUAGE"]

def clean(inputString):
    inputString = re.sub(r"http\S+", "", inputString)
    inputString = re.sub(r"@\S+", "", inputString)
    printable = set(string.printable)
    filter(lambda x: x in printable, inputString)
    return inputString.encode('ascii', 'ignore').decode('ascii')

def wikicategories(category):
    page_py = wiki_wiki.page(category)
    if len(category) > 2 and page_py.exists() and ("refer to:" != page_py.summary[-9:]):
        return True
    return False

userId = set()
itemId = set()
i = 0

def addDataRow(userid,item,rating,csvwriter):
    csvrow = [userid,item,rating]
    csvwriter.writerow(csvrow)

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def recommendItemForUser(username):
    user = api.get_user(username)
    print(user)
    userid = -1;
    statuses = api.user_timeline(
        user_id=userid, include_rts=False, exclude_replies=True, tweet_mode="extended", count=100)
    for status in statuses:
        target_tweet = clean(status.full_text)
        blob = TextBlob(target_tweet, pos_tagger=nltk_tagger)
        if True:
            try:
                print(status.full_text)
                doc = nlp("u"+clean(status.full_text));
                # sentiment analysis here
                keywords = blob.pos_tags
                for taggedTuple in keywords:
                    keyword = taggedTuple[0]
                    tag = taggedTuple[1]
                    if tag in good_PoS_Tags and wikicategories(keyword.lower()) and keyword.lower() != "gift":
                        itemId.add(keyword)
                        line_prepender("user-id-sentiment-category_and_score", "-1,"+keyword + "," + blob.sentiment.polarity)

                for ent in doc.ents:
                    if ent.label_ in good_labels:
                            itemId.add(ent.text)
                            print("Entity:" + ent.text + ent.label_)
                            line_prepender("user-id-sentiment-category_and_score", "-1,"+ent.text + "," + ent.text)

                if len(status.entities.get("media", "")) != 0:
                    imageList = status.entities.get("media", "");
                    imageurl = imageList[0].get("media_url", "")
                    with urllib.request.urlopen(imageurl) as url:
                        q = urllib.request.urlretrieve(imageurl, "local-filename.jpg");
                        detections = detector.detectObjectsFromImage(
                            input_image=os.path.join(execution_path, "local-filename.jpg"),
                            output_image_path=os.path.join(execution_path, "imagenew.jpg"))
                        os.remove("imagenew.jpg")
                        os.remove("local-filename.jpg")
                        for eachObject in detections:
                            if searcher.searchTaxMap(keyword['text']):
                                    line_prepender("user-id-sentiment-category_and_score", "-1,"+eachObject["name"] + "," + ent.text)

            except:
                response = {};
                print("tweet has unsupported languages")








# for result in tweets:
#
#     if result.user.id in userId:
#         continue
#     else:
#         userId.add(result.user.id)
#
#     statuses = tweepy.Cursor(api.user_timeline,
#                              user_id=result.user.id, include_rts=False, exclude_replies=True, tweet_mode="extended").items(5)
#     addDataRow(i, result.user.name, result.user.id, userwriter)
#     for status in statuses:
#         target_tweet = clean(status.full_text)
#         blob = TextBlob(target_tweet, pos_tagger=nltk_tagger)
#         if (True):
#             try:
#                 print(status.full_text)
#                 doc = nlp("u"+clean(status.full_text));
#                 # sentiment analysis here
#                 keywords = blob.pos_tags
#                 for taggedTuple in keywords:
#                     keyword = taggedTuple[0]
#                     tag = taggedTuple[1]
#                     if tag in good_PoS_Tags and wikicategories(keyword.lower()) and keyword.lower() != "gift":
#                         itemId.add(keyword)
#                         addDataRow(i, keyword, blob.sentiment.polarity, writer)
#                         addDataRow(i, keyword, "", itemwriter)
#
#                 for ent in doc.ents:
#                     if ent.label_ in good_labels:
#                         try:
#                             itemId.add(ent.text)
#                             print("Entity:" + ent.text + ent.label_)
#                             addDataRow(i, ent.text, blob.sentiment.polarity, writer)
#                         except:
#                             print("Entity:" + ent.text+ent.label_)
#                             addDataRow(i, ent.text, blob.sentiment.polarity, writer)
#
#                 if len(status.entities.get("media", "")) != 0:
#                     imageList = status.entities.get("media", "");
#                     imageurl = imageList[0].get("media_url", "")
#                     with urllib.request.urlopen(imageurl) as url:
#                         q = urllib.request.urlretrieve(imageurl, "local-filename.jpg");
#                         detections = detector.detectObjectsFromImage(
#                             input_image=os.path.join(execution_path, "local-filename.jpg"),
#                             output_image_path=os.path.join(execution_path, "imagenew.jpg"))
#                         os.remove("imagenew.jpg")
#                         os.remove("local-filename.jpg")
#                         for eachObject in detections:
#                             if searcher.searchTaxMap(keyword['text']):
#                                 try:
#                                     itemId.add(keyword['text'])
#                                     addDataRow(i, eachObject["name"], blob.sentiment.polarity, writer)
#                                 except:
#                                     addDataRow(i, eachObject["name"], blob.sentiment.polarity, writer)
#             except:
#                 response = {};
#                 print("tweet has unsupported languages")
#     i += 1
#     print(i)
# writefile.close()
# userwritefile.close()
# itemwritefile.close()



