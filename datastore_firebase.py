import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class DataStoreFireBase:

    cred = None
    db = None
    tweetDataTableName = u'tweetData'
    twitterScroreTableName = u'twitter_scores'    
    retweetsAndRepliesTableName = u'retweets_replies'

    def __init__(self):   
        self.cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()
    
    def checkIfRecordExists(self, tweet_id, twitter_handle):
        tweetDataCollection = self.db.collection(self.tweetDataTableName)
        doc_ref = tweetDataCollection.where(u'tweet_id', u'==', tweet_id).where(u'angle_twitter_handle', u'==', twitter_handle).get()
        if len(doc_ref) > 0:
            return doc_ref[0].exists
        else:
            return False

    def saveRewardDetails(self, tweetData):
        if tweetData['tweet_id'] != None:
            tweetDataCollection = self.db.collection(self.tweetDataTableName)
            doc_ref = tweetDataCollection.where(u'tweet_id', u'==', tweetData['tweet_id']).where(u'angle_twitter_handle', u'==', tweetData['angle_twitter_handle']).get()
            if len(doc_ref) == 0:
                #print(f" add {tweetData}")
                tweetDataCollection.document().set(tweetData)
            else:
                #print(f"update {tweetData}")
                for doc in doc_ref:
                    #print(doc.id)
                    tweetDataCollection.document(doc.id).update(tweetData) 

    def saveSAS(self, score_data):
        if score_data['twitter_handle'] != None:
            twitterScoresDataCollection = self.db.collection(self.twitterScroreTableName)
            doc_ref = twitterScoresDataCollection.where(u'twitter_handle', u'==', score_data['twitter_handle'].lower()).get()
            if len(doc_ref) == 0:
                #print(f" add {tweetData}")
                twitterScoresDataCollection.document().set(score_data)
            else:
                #print(f"update {tweetData}")
                for doc in doc_ref:
                    #print(doc.id)
                    twitterScoresDataCollection.document(doc.id).update(score_data)

    def getSAScore(self, twitter_handle):
        twitterScoresDataCollection = self.db.collection(self.twitterScroreTableName)
        doc_ref = twitterScoresDataCollection.where(u'twitter_handle', u'==', f'{twitter_handle.lower()}').get()
        if len(doc_ref) > 0:
            docDict = doc_ref[0].to_dict()
            #print(f"SAS from database {docDict}")
            if 'sa_score' in docDict:
                return docDict['sa_score']
            else:
                return None
        else:
            #print(f'getSAScore None {twitter_handle}')
            return None
    def saveBotScore(self, bot_data):
        if bot_data['twitter_user_id'] != None:
            twitterScoresDataCollection = self.db.collection(self.twitterScroreTableName)
            doc_ref = twitterScoresDataCollection.where(u'twitter_user_id', u'==', bot_data['twitter_user_id']).get()
            if len(doc_ref) == 0:
                #print(f" add {tweetData}")
                twitterScoresDataCollection.document().set(bot_data)
            else:
                #print(f"update {tweetData}")
                for doc in doc_ref:
                    #print(doc.id)
                    twitterScoresDataCollection.document(doc.id).update(bot_data)

    def getBotScore(self, twitter_user_id):
        twitterScoresDataCollection = self.db.collection(self.twitterScroreTableName)
        doc_ref = twitterScoresDataCollection.where(u'twitter_user_id', u'==', f'{twitter_user_id}').get()
        if len(doc_ref) > 0:
            docDict = doc_ref[0].to_dict()
            #print(f"SAS from database {docDict['sa_score']} - {docDict['twitter_handle']}")
            if 'bot_score' in docDict:
                return docDict['bot_score']            
            else:
                return None
        else:
            #print(f'getSAScore None {twitter_handle}')
            return None

    def saveRetweetOrReply(self, tweetData):
        if tweetData['tweet_id'] != None and tweetData['screen_name'] != None:
            tweetDataCollection = self.db.collection(self.retweetsAndRepliesTableName)
            doc_ref = tweetDataCollection.where(u'tweet_id', u'==', tweetData['tweet_id']).where(u'screen_name', u'==', tweetData['screen_name']).get()
            if len(doc_ref) == 0:
                #print(f" add {tweetData}")
                tweetDataCollection.document().set(tweetData)
            else:
                #print(f"update {tweetData}")
                for doc in doc_ref:
                    #print(doc.id)
                    tweetDataCollection.document(doc.id).update(tweetData)
    
    def getRetweetOrReply(self, tweet_id, screen_name):
        tweetDataCollection = self.db.collection(self.retweetsAndRepliesTableName)
        doc_ref = tweetDataCollection.where(u'tweet_id', u'==', tweet_id).where(u'screen_name', u'==', screen_name).get()
        if len(doc_ref) > 0:
            docDict = doc_ref[0].to_dict()
            if 'bot_score' in docDict:
                return docDict
            else:
                return None
        else:
            return None
    
    def getAlRetweetsAndReplies(self, parent_tweet_id):
        tweetDataCollection = self.db.collection(self.retweetsAndRepliesTableName)
        doc_ref = tweetDataCollection.where(u'parent_tweet_id', u'==', parent_tweet_id).get()
        if len(doc_ref) > 0:
            retweetsAndReplies = []
            for doc in doc_ref:
                retweetsAndReplies.append(doc.to_dict())
            return retweetsAndReplies
        else:
            return []