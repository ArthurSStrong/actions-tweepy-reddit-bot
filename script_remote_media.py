#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Takes the last 10 user tweets and posts them to Reddit if they include one image."""

import os
import praw
import tweepy
from datetime import datetime
from datetime import timedelta

CLIENT_ID = (os.environ['CLIENT_ID'] if 'CLIENT_ID'
             in os.environ else '')
CLIENT_SECRET = (os.environ['CLIENT_SECRET'] if 'CLIENT_SECRET'
                 in os.environ else '')
USERNAME = (os.environ['USERNAME'] if 'USERNAME'
            in os.environ else '')
PASSWORD = (os.environ['PASSWORD'] if 'PASSWORD'
            in os.environ else '')

CONSUMER_KEY = (os.environ['CONSUMER_KEY'] if 'CONSUMER_KEY'
                in os.environ else '')
CONSUMER_SECRET = (os.environ['CONSUMER_SECRET'] if 'CONSUMER_SECRET'
                   in os.environ else ''
                   )
ACCESS_TOKEN = (os.environ['ACCESS_TOKEN'] if 'ACCESS_TOKEN'
                in os.environ else ''
                )
ACCESS_TOKEN_SECRET = (os.environ['ACCESS_TOKEN_SECRET'
                       ] if 'ACCESS_TOKEN_SECRET'
                       in os.environ else ''
                       )
SUBREDDIT = 'lazonacero'


STOPWORDS = './stopwords.txt'
TUSERS = './tusers.txt'
APPROVED_TAGS = './approved_tags.txt'


def load_file(file):
    """Load the log file and creates it if it doesn't exist.

     Parameters
    ----------
    file : str
        The file to write down
    Returns
    -------
    list
        A list of urls.
    """

    try:
        with open(file, 'r', encoding='utf-8') as temp_file:
            return temp_file.read().splitlines()
    except Exception:

        with open(file, 'w', encoding='utf-8') as temp_file:
            return []


def get_tweets(api, t_user):
    """Get tweets from api.

    Parameters
    ----------
    api : tweepy.API
        twitter api object
    t_user : str
        The username of twitter you want to get.

    Returns
    -------
    list
        A list of tweets.

    """

    # test authentication

    try:
        api.verify_credentials()
        print('Authentication OK')
    except:
        print('Error during authentication')
        exit()

    user = api.get_user(t_user)
    tweets = api.user_timeline(screen_name=user.screen_name, count=10,
                               include_rts=False, exclude_replies=True,
                               tweet_mode='extended')
    return tweets[:10]


def init_bot():
    """Read twwts get images and submit to subreddit."""

    # We create the Reddit instance.

    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         username=USERNAME, password=PASSWORD,
                         user_agent='testscript by /u/disentibot')

    # Authenticate to Twitter

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Create API object

    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    tusers = load_file(TUSERS)

    tweets = list()

    for tuser in tusers:
        tweets = tweets + get_tweets(api, tuser)

    # Datetime tolerance, set to 4 hours

    tolerance_time = datetime.today() - timedelta(hours=6)

    stopwords = load_file(STOPWORDS)
    approved_tags = load_file(APPROVED_TAGS)

    for tweet in reversed(tweets):
        try:
            image_count = len(tweet.extended_entities['media'])
            print('media number: {}  created_at: {}'.format(image_count, tweet.created_at))

            title = ' '.join([item for item in tweet.full_text.split(' ') if 'https' not in item]).replace('.', '')
            title = ' '.join(title.replace('\r', '. ').replace('\n', '. ').split()).replace("@", "")

            if  any(stopword.lower() in title.lower() for stopword in stopwords):
                continue

            if  any(approved_tag.lower() in title.lower() for approved_tag in approved_tags) and (image_count and image_count < 2 and tweet.created_at >= tolerance_time):

                print("submitting {}".format(title))
                reddit.subreddit(SUBREDDIT).submit(title=title,
                        url=tweet.entities['media'][0]['media_url'],
                        flair_id='d58a493c-22b5-11eb-9842-0ef5edbfd6f9')

        except Exception as e:
            print(e)
            continue        


if __name__ == '__main__':

    init_bot()
