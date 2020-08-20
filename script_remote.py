"""Takes the last 3 user tweets and posts them to Reddit."""
import os
import praw
import tweepy


CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

LOG_FILE = "./processed_ids.txt"


def load_log():
    """Loads the log file and creates it if it doesn't exist.

    Returns
    -------
    list
        A list of urls.

    """

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as temp_file:
            return temp_file.read().splitlines()

    except Exception:
        with open(LOG_FILE, "w", encoding="utf-8") as temp_file:
            return []


def update_log(teet_id):
    """Updates the log file.

    Parameters
    ----------
    teet_id : str
        The teet_id to log.

    """

    with open(LOG_FILE, "a", encoding="utf-8") as temp_file:
        temp_file.write(teet_id + "\n")


def get_tweets(api):
    """Gets tweets from api.

    Returns
    -------
    list
        A list of tweets.

    """
    # test authentication
    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")
        exit()

    user = api.get_user("LZCOficial")
    tweets = api.user_timeline(screen_name=user.screen_name, count=10, include_rts=True, exclude_replies=True, tweet_mode='extended')
    return user, tweets[:3]


def init_bot():
    """Initialize bots and read tweets."""

    # We create the Reddit instance.
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, username=USERNAME, password=PASSWORD, user_agent="testscript by /u/larry3000bot")

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    user, tweets = get_tweets(api)

    for tweet in tweets:
        log = load_log()
        if str(tweet.id) not in log:
            print("Posting ID: {}".format(tweet.id))
            url = "https://twitter.com/{0}/status/{1}".format(user.screen_name, tweet.id)
            title = " ".join([item for item in tweet.full_text.split(" ") if "https" not in item])
            title = " ".join(title.replace('\r', ' ').replace('\n', ' ').split())

            reddit.subreddit('lazonacero').submit(
                    title=title, url=url)
            update_log(str(tweet.id))


if __name__ == "__main__":

    init_bot()
