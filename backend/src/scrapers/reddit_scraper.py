import praw
import pandas as pd


def scrape_reddit(keywords, subreddits=None, limit=50):
    if subreddits is None:
        subreddits = ['UCSB', 'SantaBarbara']
    reddit = praw.Reddit(
        client_id='CLIENT_ID',  # For local development, replace with client id associated with your developer reddit
        # account
        client_secret='CLIENT_SECRET',  # For local development, replace with client secret associated with your
        # developer reddit account
        user_agent='account_name'  # Reddit agent name
    )

    data = []

    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        print(f"Scanning r/{sub}...")

        for keyword in keywords:
            for post in subreddit.search(keyword, sort='relevance', limit=limit):
                data.append({
                    'source': 'Reddit',
                    'subreddit': sub,
                    'keyword': keyword,
                    'title': post.title,
                    'url': post.url,
                    'score': post.score,
                    'text': post.selftext[:200]
                })

    return data
