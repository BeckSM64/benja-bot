import snscrape.modules.twitter as sntwitter

class TweetFetcher:
    def __init__(self):

        # List of tweets
        self.tweetsList = []

    def getTweets(self, username):

        # Using TwitterSearchScraper to scrape data and append tweets to list
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper('from:' + username).get_items()): # Declare a username 

            # Number of tweets to scrape
            if i > 20000:
                break
            
            # Add tweet list to list of tweets
            # Each tweet is a list containing date, id, content, and username
            self.tweetsList.append([tweet.date, tweet.id, tweet.content, tweet.username]) # Declare the attributes to be returned

        # Write to text file
        with open('tweetsBackup.txt', 'w') as f:
            for item in self.tweetsList:
                f.write("%s\n" % item)

        # Return the list of list of tweets
        return self.tweetsList
