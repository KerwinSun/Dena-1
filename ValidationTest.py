import tweepy
import SemanticNetRecomender2WikiepdiaAPI

consumer_key = "uqKb1h9prIwbAVCqocBuqInFs"
consumer_secret = "EXlWGr7VFTGJ00116M25mDWyNveORVkHVPGXHaAOsg1lwFUQn8"
access_token = "2388347288-uEH2UbQnr2uZYCZDuvh93wD8UHZ3PMB15diH9tK"
access_token_secret ="RCXSN3rj4m04ECekNo3DnF2u7B4G7AJauZXs3DmbX14dc"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#find posts that mention gifts
tweets = tweepy.Cursor(api.search,
                       q='-RT #greatgift', lang="en").items(1);

for tweet in tweets:
    print(tweet)
    tweetText = tweet.text
#extract entities from posts
    dict_tuple = SemanticNetRecomender2WikiepdiaAPI.doTextAnalysis(tweetText)
    print("TARGET CATEGORIES")
    print(dict_tuple[0])
    print(dict_tuple[1])

# use reccomender to find gifts for that user
    predicted_tuple = SemanticNetRecomender2WikiepdiaAPI.doUserAnalysis(tweet.author.screen_name, tweet.id_str)
    print("PREDICTED CATEGORIES")
    print(predicted_tuple[0])
    print(predicted_tuple[1])

#check for overlap between reccomendation and target