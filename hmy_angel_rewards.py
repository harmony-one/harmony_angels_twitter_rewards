import requests
import oauth2 as oauth 
import json
import botometer
from sas import FollowerWonk
from datastore_firebase import DataStoreFireBase
from secretes import Secretes
import tweepy
import csv
from tweepy.parsers import JSONParser
import random
import threading
import requests
import time
from sys import argv
import configparser

class ScanAngelReTweet:

    twitterConsumerApiKey = Secretes.twitterConsumerApiKey
    twitterConsumerApiSecret = Secretes.twitterConsumerApiSecret
    twitterAccessToken = Secretes.twitterAccessToken
    twitterAccessTokenSecret =  Secretes.twitterAccessTokenSecret
    rapidAPIKey = Secretes.rapidAPIKey

    consumer = None
    twitterToken = None
    client = None
    bom = None
    dataStore = None
    search_headers = None
    user_id = None
    harmonyTeamProfiles = list()
    angelProfileIds = list()
    angelProfiles = {}
    bot_score_ids = []
    sas_score_ids = []
    child_tweet_ids = []
    child_tweet_user = {}

    def __init__(self):
        self.twitterToken = oauth.Token(self.twitterAccessToken, self.twitterAccessTokenSecret)
        self.consumer = oauth.Consumer(self.twitterConsumerApiKey, self.twitterConsumerApiSecret)
        twitter_app_auth = {
            'consumer_key': self.twitterConsumerApiKey,
            'consumer_secret': self.twitterConsumerApiSecret,
            'access_token': self.twitterAccessToken,
            'access_token_secret': self.twitterAccessTokenSecret,
        }
        self.client = oauth.Client(self.consumer, self.twitterToken)
        self.search_headers = {
            'Authorization': 'Bearer {}'.format(Secretes.twitterBearerToken)    
        }
        botometer_api_url = 'https://botometer-pro.p.rapidapi.com'
        self.bom = botometer.Botometer(botometer_api_url=botometer_api_url, wait_on_ratelimit=True, rapidapi_key=self.rapidAPIKey, **twitter_app_auth)
        self.dataStore = DataStoreFireBase()
        self.harmonyTeamProfiles = ['stse', 'rongjianlan', 'leo_hao', 'denni_swon', 'gupadhyaya', 'andrewistyping', 'cottontail2000', 'thechaindev', 'xiaopen01917726', 'janetlharmony', 'danielvdmaden', 'potvik1', 'haodi2best', 
            'jackythecoder', 'sahildewan', 'nickwh8te', 'lijiang2087', 'chaowen28', 'dirschmidt', 'nickostopoulos', 'gizemcakil', 'maggiewangharm1', 'niteesh_harmony', 'vasilich_nick', 'mannymcoy', 'sonnyneverknows', 
            'cb_cryptalk', 'danboyden', 'drop101001', 'alex_yatesalex', 'flicker05091469', 'alex_kretsch', 'yishuangc', 'minhdoan82', 'john_a_whitton', 'bwu2sfu', 'mattdlockyer', 'chaosma000', 'edgararout', 'harmonyyuyi', 
            'cem_fahli', 'vbieberin', 'nicolasburtey', 'ametaheuristic', 'astralblue', 'garlamwon', 'sarahn_harmony', 'manish0338', 'm_dansker', 'john_lamu', 'x_chickens', 'larissa_bean7', 'johnlamharmony', 'yongxinjzhou', 
            'renewwen', 'mindpop3', 'danboyden', 'drop101001', 'iscirlet', 'ibruno_marshall', 'sophoah', 'jb273_jurgen', 'yelllowsin', 'mindstyle85', 'mirrormirage0', 'sebastianj', 'yeiliowsin','wholesum', 'mr_vavilon', 
            'HarmonyValidatr', 'spi41619364', 'da_prost0', 'tweet4jack', 'edixonve', 'chang8317', 'uptemplates', 'shapuillouwa', 'zhanglianghui', 'pizza_pizza3141', 'zelpresso', 'trumhemcut', 'yginting']

    def calculateRewards(self, sa_score):
        base = 12.5
        variable = pow(2, ((sa_score-20) / 10))
        return base * variable
    
    def getOneAddressFromUrl(self, bioUrl):
        if "harmony.one/#" in bioUrl:
            parts = bioUrl.split("#")
            if len(parts) > 1:
                oneAddress = parts[1].split("=")
                if len(oneAddress) > 1:
                    return oneAddress[1]
        return ""

    def updateBOTscore(self, twitterUserIds):
        for tUid in twitterUserIds:
            bot_score = self.dataStore.getBotScore(tUid)
            if bot_score == None:
                result = self.bom.check_account(tUid)                
                bot_score = result['cap']['english']
                print(f'{tUid} - {bot_score}')
                self.dataStore.saveBotScore({
                    'twitter_user_id' : tUid,
                    'bot_score' : bot_score
                })
    
    def updateSAStoProfiles(self, scores, handles):
        for score in scores:
            self.dataStore.saveSAS({
                'twitter_handle' : score['screen_name'].lower(),
                'sa_score' : score['social_authority']
            })
    
    def updateSAS(self, profile_handles):
        handles = ''
        for pid in profile_handles:
            twitter_handle = pid
            sa_score = self.dataStore.getSAScore(twitter_handle)
            #print(f'{pid} - {sa_score}')
            if(sa_score == None):
                sa_score = -1
            if twitter_handle != '' and sa_score < 0:
                if handles == '':
                    handles = f'{twitter_handle}'
                else:
                    handles = f'{handles},{twitter_handle}'
                parts = handles.split(",")
                if len(parts) == 25: 
                    try:
                        print(handles)
                        scores = FollowerWonk.social_authority(handles)
                        #print(scores)
                        self.updateSAStoProfiles(scores, handles)           
                        handles = ''
                    except Exception as ex:
                        handles = ''
                        print(f'FollowerWonk exception for twitter handle {handles} - {ex}')
                        continue
        if(handles != ''):
            try:
                print(f"else {handles}")
                scores = FollowerWonk.social_authority(handles)     
                #print(scores)
                self.updateSAStoProfiles(scores, handles)          
                handles = ''
            except Exception as ex:
                handles = ''
                print(f'FollowerWonk exception for twitter handle {handles} - {ex}')

    def scanRetweetStandard(self, tweet_dict, query):
        tweet_id = tweet_dict['tweet_id']
        user_id = tweet_dict['twitter_id']
        screen_name = tweet_dict['screen_name']
        retweet_details = []
        if 'retweet_details' in tweet_dict:
            retweet_details = tweet_dict['retweet_details']
        if retweet_details == None:
            retweet_details = []
        url = f'https://api.twitter.com/1.1/statuses/retweets/{tweet_id}.json?count=100&result_type=recent'
        print(f'Child tweets retweets url {url}')  
        contents = requests.get(url, headers=self.search_headers)
        jsonResponse = contents.json()
        
        if "error" in jsonResponse or len(jsonResponse) == 0 or "errors" in jsonResponse:
            print(jsonResponse)
            return
        print(f'retweet count {len(jsonResponse)}')            
        for rTweet in jsonResponse:
            #print(f"main rewteet {tweet_id} {rTweet['user']['screen_name']}  {rTweet['is_quote_status']}")
            processTweet = True
            if processTweet:
                if not (rTweet['user']['screen_name']).lower() in self.harmonyTeamProfiles:
                    child_tweet_dict = {
                        "retweet_user_id" : rTweet['user']["id_str"],
                        "retweet_user_screen_name" : rTweet['user']["screen_name"],
                        "engagement" : "retweet",
                        "retweet_id" : rTweet["id_str"]}
                    if not child_tweet_dict in retweet_details:
                        print(child_tweet_dict)
                        retweet_details.append(child_tweet_dict)         
                    sas = self.dataStore.getSAScore(rTweet['user']["screen_name"])
                    if sas == None:
                        self.sas_score_ids.append(rTweet['user']["screen_name"])
                    bot_score = self.dataStore.getBotScore(rTweet['user']["screen_name"])
                    if bot_score == None:
                        self.bot_score_ids.append(rTweet['user']["id_str"])

        url = f'https://api.twitter.com/1.1/search/tweets.json?q={query} OR @{screen_name}&since_id={tweet_id}&count=100&result_type=recent&tweet_mode=extended'
        print(f'Child tweets search url {url}')  
        contents = requests.get(url, headers=self.search_headers)
        jsonResponse = contents.json()
        
        if "error" in jsonResponse or len(jsonResponse) == 0 or "errors" in jsonResponse:
            print(jsonResponse)
            return
        if 'statuses' in jsonResponse:
            print(f'retweet count statuses {len(jsonResponse["statuses"])}')            
            for rTweet in jsonResponse['statuses']:
                #print(f"main rewteet {tweet_id} {rTweet['user']['screen_name']}  {rTweet['is_quote_status']}")
                engagementType = 'retweet'
                processTweet = False
                if 'is_quote_status' in rTweet:
                    if 'quoted_status_id_str' in rTweet:
                        if rTweet['is_quote_status']:
                            if rTweet['quoted_status_id_str'] == tweet_id:
                                processTweet = True
                                engagementType = 'retweet'

                if 'in_reply_to_user_id_str' in rTweet:
                    if rTweet['in_reply_to_user_id_str'] == user_id:
                        processTweet = True
                        engagementType = 'reply'
                
                if 'retweeted_status' in rTweet:
                    if rTweet['retweeted_status']['in_reply_to_status_id_str'] == tweet_id:
                        processTweet = True
                        engagementType = 'retweet'            
                if 'retweeted_status' in rTweet:
                    if rTweet['retweeted_status']['in_reply_to_status_id_str'] == tweet_id:
                        processTweet = True

                if processTweet:
                    if not (rTweet['user']['screen_name']).lower() in self.harmonyTeamProfiles:
                        child_tweet_dict = {
                            "retweet_user_id" : rTweet['user']["id_str"],
                            "retweet_user_screen_name" : rTweet['user']["screen_name"],
                            "engagement" : engagementType,
                            "retweet_id" : rTweet["id_str"]}
                        if not child_tweet_dict in retweet_details:
                            print(child_tweet_dict)
                            retweet_details.append(child_tweet_dict)         
                        sas = self.dataStore.getSAScore(rTweet['user']["screen_name"])
                        if sas == None:
                            self.sas_score_ids.append(rTweet['user']["screen_name"])
                        bot_score = self.dataStore.getBotScore(rTweet['user']["screen_name"])
                        if bot_score == None:
                            self.bot_score_ids.append(rTweet['user']["id_str"])

        tweet_dict['retweet_details'] = retweet_details
        #print(f'retweet details {retweet_details}')
        self.dataStore.saveRetweetOrReply(tweet_dict)
    
    def startTweetScan(self, tweet_id, user_id, screen_name, query):
        
        self.get_tweet_replys(tweet_id, screen_name, query)
        url = f'https://api.twitter.com/1.1/search/tweets.json?q={query} OR @{screen_name}&since_id={tweet_id}&count=100&result_type=recent&tweet_mode=extended'
        print(f'main url {url}')
        contents = requests.get(url, headers=self.search_headers)
        jsonResponse = contents.json()
        angel_handles = []
        if "error" in jsonResponse:
            print(jsonResponse)
            return
        print(f'main retweet count {len(jsonResponse["statuses"])}')            
        for rTweet in jsonResponse["statuses"]:
            #print(f"main rewteet {tweet_id} {rTweet['user']['screen_name']}  {rTweet['is_quote_status']}")
            engagementType = 'retweet'
            processTweet = False
            if rTweet['is_quote_status']:
                if 'quoted_status_id_str' in rTweet:
                    if rTweet['quoted_status_id_str'] == tweet_id:
                        processTweet = True
                        engagementType = 'retweet'

            if rTweet['in_reply_to_user_id_str'] == user_id:
                processTweet = True
                engagementType = 'reply'
            
            if 'retweeted_status' in rTweet:
                if rTweet['retweeted_status']['in_reply_to_status_id_str'] == tweet_id:
                    processTweet = True
                    engagementType = 'retweet'

            if processTweet:
                if not (rTweet['user']['screen_name']).lower() in self.harmonyTeamProfiles:
                    if not rTweet['user']["id_str"] in self.angelProfileIds:
                        if 'url' in rTweet['user']['entities']:
                            if(len(rTweet['user']['entities']['url']['urls']) > 0):
                                    bioUrl = rTweet['user']['entities']["url"]['urls'][0]['expanded_url']
                                    if bioUrl != None:
                                        print(f"{rTweet['user']['screen_name']} - {bioUrl}")
                                        oneAddress = self.getOneAddressFromUrl(bioUrl)
                                        if oneAddress.startswith("one1"):
                                            tweet_dict = {
                                                'tweet_id' : rTweet["id_str"],
                                                'parent_tweet_id' : tweet_id,
                                                'name' : rTweet['user']['name'],
                                                'screen_name' : rTweet['user']['screen_name'],
                                                'oneAddress' : oneAddress,
                                                'engagement' : engagementType,
                                                'twitter_id' : rTweet['user']['id_str']
                                            }
                                            self.angelProfiles[f'{rTweet["user"]["id_str"]}'] = tweet_dict
                                            self.child_tweet_ids.append(rTweet["id_str"])
                                            self.child_tweet_user[rTweet["id_str"]] = {
                                                'user_id' :  rTweet['user']["id_str"],
                                                'screen_name' : rTweet['user']['screen_name']
                                            }
                                            self.dataStore.saveRetweetOrReply(tweet_dict)
                                            angel_handles.append(rTweet['user']['screen_name'])
                                            self.angelProfileIds.append(rTweet['user']["id_str"])
                                            sas = self.dataStore.getSAScore(rTweet['user']["screen_name"])
                                            if sas == None:
                                                self.sas_score_ids.append(rTweet['user']["screen_name"])
                                            bot_score = self.dataStore.getBotScore(rTweet['user']["screen_name"])
                                            if bot_score == None:
                                                self.bot_score_ids.append(rTweet['user']["id_str"])
                                             
        retweetsAndReplies = self.dataStore.getAlRetweetsAndReplies(tweet_id)
        for tweet_dict in retweetsAndReplies:
            self.scanRetweetStandard(tweet_dict, query)

        #print(f' Profile Ids {self.angelProfiles}')
        #print(f' Profiles {self.angelProfileIds} {len(self.angelProfileIds)}')
        #print(f' Bot Score Ids {self.bot_score_ids} SAS score Ids {self.sas_score_ids}')

    def get_tweet_replys(self, tweet_id, screen_name, query):
    
        auth = tweepy.OAuthHandler(self.twitterConsumerApiKey, self.twitterConsumerApiSecret)
        auth.set_access_token(self.twitterAccessToken, self.twitterAccessTokenSecret)
        api = tweepy.API(auth)
        
        replies = tweepy.Cursor(api.search, q='to:{}'.format(screen_name),                                
                                since_id=tweet_id, result_type='recent', tweet_mode='extended').items()
        noReplies = 0
        count = 0
        angel_handles = []
        while True:
            try:
                reply = replies.next()
                if not hasattr(reply, 'in_reply_to_status_id_str'):
                    continue
                if reply.user.id_str in self.angelProfileIds:
                    continue
                if reply.user.screen_name.lower() in self.harmonyTeamProfiles:
                    continue
                if not hasattr(reply.user.entities, 'url'):
                    bioUrl = reply.user.entities['url']['urls'][0]['expanded_url']
                    oneAddress = self.getOneAddressFromUrl(bioUrl)
                    if oneAddress.startswith("one1"):
                        tweet_dict = {
                            'tweet_id' : reply.id_str,
                            'parent_tweet_id' : tweet_id,
                            'name' : reply.user.name,
                            'screen_name' : reply.user.screen_name,
                            'oneAddress' : oneAddress,
                            'engagement' : 'reply',
                            'twitter_id' : reply.user.id_str
                        }
                        self.angelProfiles[f"{reply.user.id}"] = tweet_dict
                        self.dataStore.saveRetweetOrReply(tweet_dict)
                        self.child_tweet_ids.append(reply.id_str)
                        self.child_tweet_user[reply.id_str] = {
                            'user_id' :  reply.user.id_str,
                            'screen_name' : reply.user.screen_name
                        }
                        sas = self.dataStore.getSAScore(reply.user.screen_name)
                        if sas == None:
                            self.sas_score_ids.append(reply.user.screen_name)
                        bot_score = self.dataStore.getBotScore(reply.user.screen_name)
                        if bot_score == None:
                            self.bot_score_ids.append(reply.user.id_str)
                        self.angelProfileIds.append(reply.user.id_str)
                        angel_handles.append(reply.user.screen_name)      
            except tweepy.RateLimitError as e:
                #print("Twitter api rate limit reached".format(e))
                continue
            except tweepy.TweepError as e:
                #print("Tweepy error occured:{}".format(e))
                break
            except StopIteration:
                break
            except Exception as e:
                #print("Failed while fetching replies {}".format(e))
                continue
        print(f"Number of replies {noReplies} total count {count}")

    def calulateFollowerEnagementReward(self, retweet_details):
        reward = 0
        countedIds = []
        for rtd in retweet_details:
            if not rtd['retweet_user_id'] in countedIds:
                sas = self.dataStore.getSAScore(rtd['retweet_user_screen_name'])
                if sas == None:
                    sas = 0
                bot_score = self.dataStore.getBotScore(rtd['retweet_user_id'])
                if bot_score == None:
                    bot_score = 0.70
                if not (sas < 20 or bot_score > 0.70):
                    reward = reward + self.calculateRewards(sas)
                countedIds.append(rtd['retweet_user_id'])
        return reward

    def calculateRewardsAndSave(self, tweet_id):
        retweetsAndReplies = self.dataStore.getAlRetweetsAndReplies(tweet_id)
        for tweet_dict in retweetsAndReplies:
            angelProfile = tweet_dict
            twitter_handle = angelProfile['screen_name']
            twitter_user_id = angelProfile['twitter_id']            
            bot_score = 0.70
            sas = self.dataStore.getSAScore(twitter_handle)
            if sas == None:
                sas = 0
            try:
                bot_score = self.dataStore.getBotScore(twitter_user_id)
                if bot_score == None:
                    result = self.bom.check_account(twitter_user_id)
                    bot_score = result['scores']['english']
                    self.dataStore.saveBotScore({
                        'twitter_handle' : twitter_handle.lower(),
                        'bot_score' : bot_score
                    })
            except:
                print(f'Rapid API exception for twitter handle {twitter_handle}')
            #if not (sas < 20 or bot_score > 1.5):
            followerEnagementReward = 0
            if 'retweet_details' in angelProfile:
                followerEnagementReward = self.calulateFollowerEnagementReward(angelProfile['retweet_details'])
            tweetData = {
                        u'tweet_id': tweet_id,
                        u'angle_twitter_id': twitter_user_id,
                        u'angle_twitter_handle': twitter_handle,
                        u'sa_score': sas,
                        u'bot_score': bot_score,
                        u'reward': self.calculateRewards(sas) + followerEnagementReward,
                        u'follower_eng_reward' : followerEnagementReward,
                        u'angel_one_address': angelProfile['oneAddress'],
                        u'engagement': angelProfile['engagement'],
                        u'child_tweet_id': angelProfile['tweet_id'],
                    }
            self.dataStore.saveRewardDetails(tweetData)
            print(f'{twitter_handle} rewards details saved')        
#            else:
#               print(f'{twitter_handle} may be a bot')   

    def process_tweet(self, tweet_id, screen_name, query):
        if self.user_id == None:
            url = f'https://api.twitter.com/1.1/users/lookup.json?screen_name={screen_name}'
            contents = requests.get(url, headers=self.search_headers)
            jsonResponse = contents.json()
            if "error" in jsonResponse:
                print(jsonResponse)
            if len(jsonResponse) > 0:
                if 'screen_name' in jsonResponse[0]:
                    if jsonResponse[0]['screen_name'] == screen_name:
                        self.user_id = jsonResponse[0]['id_str']
        if self.user_id == '' or self.user_id == None:
            print('Twitter user id error, script not started')
            return
        self.sas_score_ids.clear()
        self.bot_score_ids.clear()
        self.startTweetScan(tweet_id, self.user_id, screen_name, query)
        self.updateSAS(self.sas_score_ids)
        self.updateBOTscore(self.bot_score_ids)
        self.calculateRewardsAndSave(tweet_id)

def stopScript(tweet_id):
    configFileName = 'script_runnint_time.config'
    config = configparser.ConfigParser()
    config.read(configFileName)
    if config != None:
        if tweet_id in config['DEFAULT']:
            start_time = float(config.get('DEFAULT', tweet_id))
            current_time = time.time()
            duration = current_time - start_time
            print(f'Duration {duration} in seconds')
            if duration >= (48 * 60 * 60):
                return True
        else:
            config['DEFAULT'] = {tweet_id: time.time()}
            with open(configFileName, 'w') as configfile:
                config.write(configfile)
    return False

scanTweet = ScanAngelReTweet()
def repeatTweetScan():
    #scanTweet.process_tweet("1299747582021971968", "1296871334929211395", "vasilich_nick", "Test2 OR test2")
    if len(argv) == 4:
        scanTweet.process_tweet(argv[1], argv[2], argv[3])
        if not stopScript(argv[1]):
            threading.Timer(1000.0, repeatTweetScan).start()
        else:
            print('Stopping the script after 48 hours')
    else:
        print('Arguments are not valid please check the arguments ex: python3 hmy_angel_rewards.py 1299747582021971968 stse "augpow"')

def main(tArgs):
    repeatTweetScan()

if __name__ == '__main__':
    main(argv)
