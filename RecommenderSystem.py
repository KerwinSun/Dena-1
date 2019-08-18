import fileinput
import os
import re
import string
import urllib

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import spacy
import turicreate
import tweepy
import wikipediaapi
from imageai.Detection import ObjectDetection
from surprise import NormalPredictor, KNNBasic
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise import SVD
from collections import defaultdict

from surprise.prediction_algorithms.matrix_factorization import SVDpp
from surprise.prediction_algorithms.slope_one import SlopeOne
from textblob import TextBlob
from textblob.en.taggers import NLTKTagger

from EbayProductFinding import getProductsForRecommender
import wikipediaapi
from TaxonomySearcher import TaxonomySearcher

# helper methods to assist in sanitising tweets before analysis
def clean(inputString):
    inputString = re.sub(r"http\S+", "", inputString)
    inputString = re.sub(r"@\S+", "", inputString)
    printable = set(string.printable)
    filter(lambda x: x in printable, inputString)
    return inputString.encode('ascii', 'ignore').decode('ascii')

def wikicategories(category):
    wiki_wiki = wikipediaapi.Wikipedia('en')
    page_py = wiki_wiki.page(category)
    if len(category) > 2 and page_py.exists() and ("refer to:" != page_py.summary[-9:]):
        return True
    return False

def line_pre_adder(filename, line_to_prepend):
    with open(filename, 'r') as original: data = original.read()
    with open(filename, 'w') as modified: modified.write(line_to_prepend + data)


def recommendItemForUser(username,number):
    consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
    consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
    access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
    access_token_secret = "RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
    wiki_wiki = wikipediaapi.Wikipedia('en')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    tweets = tweepy.Cursor(api.search,
                           q="gift", lang="en", result_type='mixed').items(45);
    execution_path = os.getcwd()
    good_PoS_Tags = ["NN", "NNS", "NNP", "NNPS"]
    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath(os.path.join(execution_path, "resnet50_coco_best_v2.0.1.h5"))
    detector.loadModel()
    searcher = TaxonomySearcher();
    nlp = spacy.load("en_core_web_lg")
    nltk_tagger = NLTKTagger()
    count = 0
    good_labels = ["PERSON", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK OF ART", "LANGUAGE"]
    user = api.get_user(username)
    print(user)
    userid = -1;
    statuses = api.user_timeline(
        user_id=user.id, include_rts=False, exclude_replies=True, tweet_mode="extended", count=100)
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
                        line_pre_adder("user-id-sentiment-category_and_score",number+","+keyword + "," + str(blob.sentiment.polarity) +"\n")

                for ent in doc.ents:
                    if ent.label_ in good_labels:
                            print("Entity:" + ent.text + ent.label_)
                            line_pre_adder("user-id-sentiment-category_and_score",number+","+ent.text + "," + str(blob.sentiment.polarity)+"\n")

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
                                    line_pre_adder("user-id-sentiment-category_and_score", number+","+eachObject["name"] + "," + str(blob.sentiment.polarity)+"\n")

            except:
                response = {};
                print("tweet has unsupported languages")




def predict(ratings, similarity, type='user'):
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        #We use np.newaxis so that mean_user_rating has same format as ratings
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
    return pred


def get_top_n(predictions, n=10):
    '''Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    '''

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


recommendItemForUser("ZO2_",-3)
print("done")
r_cols = ['user_id', 'item_id', 'rating']
ratings = pd.read_csv('user-id-sentiment-category_and_score', names=r_cols)
items = pd.read_csv('item-id', names=['item_id', 'item_name', 'placeholder'])
users = pd.read_csv('user-id',names=['user_id', 'user_name', 'twitter_id'])
# n_items = ratings.item_id.unique().shape[0]
# n_users = ratings.user_id.unique().shape[0]
# data_matrix = np.zeros((n_users, n_items))
# train_data = turicreate.SFrame(ratings)
#
#
# #Training the model
# item_sim_model = turicreate.item_similarity_recommender.create(train_data, user_id='user_id', item_id='item_id', target='rating', similarity_type='cosine')
#
# #Making recommendations
# item_sim_recomm = item_sim_model.recommend(users=[1,2,3,4,5],k=5)
# item_sim_recomm.print_rows(num_rows=25)


reader = Reader(rating_scale=(-1, 1))
data = Dataset.load_from_df(ratings[['user_id', 'item_id', 'rating']], reader)
trainset = data.build_full_trainset();
cross_validate(NormalPredictor(), data, cv=2)
algo = KNNBasic()
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
algo.fit(trainset)
testset = trainset.build_anti_testset()
predictions = algo.test(testset)
top_n = get_top_n(predictions, n=5)
print("TEST")
i = 0;
# Print the recommended items for each user
for uid, user_ratings in top_n.items():
    if i == 2:
        break
    else:
        print(uid, [iid for (iid, _) in user_ratings])
        getProductsForRecommender(user_ratings)
        i += 1

# for line in ratings.itertuples():
#     data_matrix[line[1]-1, line[2]-1] = line[3]
#
# user_similarity = pairwise_distances(data_matrix, metric='cosine')
# item_similarity = pairwise_distances(data_matrix.T, metric='cosine')
# user_prediction = predict(data_matrix, user_similarity, type='user')
# item_prediction = predict(data_matrix, item_similarity, type='item')
# print(user_prediction)
# print(item_prediction)

#0 ['Festival', 'Enter', 'Lmao', 'Lol', 'beagle']
# -1 ['Intersect', 'birthday', 'Win Tickets +', 'Lol', 'Spinach Wraps']
# -1 ['Six', 'Awakening', 'Years', 'Greatest', 'Ever']
# -1 ['Optimum', 'Nutrition', 'Protein', 'Whipped', 'Bites']
