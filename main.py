import os
import praw
import re
from collections import Counter


def create_reddit_client():
    """
    Configure Reddit API access using environment variables.

    :return: An authenticated Reddit client instance.
    """
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent='Reddit Ticker Trends 2.0'
    )


def extract_stock_symbols(text, valid_symbols=None):
    """
    Extract stock symbols from text.

    :param text: The input text containing potential stock symbols.
    :param valid_symbols: A list or set of valid stock symbols for validation (optional).
    :return: A list of extracted stock symbols.
    """
    stock_pattern = r'\b[A-Z]{2,5}\b'
    symbols = re.findall(stock_pattern, text)

    if valid_symbols:
        symbols = [symbol for symbol in symbols if symbol in valid_symbols]

    return symbols


def process_posts_and_comments(subreddit, reddit):
    """
    Extract stock symbols from posts and comments in a subreddit.

    :param subreddit: The name of the subreddit to process.
    :param reddit: The authenticated Reddit client instance.
    :return: A list of stock symbols mentioned in posts and comments.
    """
    symbols = []

    for submission in reddit.subreddit(subreddit).search("ETF", limit=100):
        symbols.extend(extract_stock_symbols(submission.title))
        symbols.extend(extract_stock_symbols(submission.selftext))

        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            symbols.extend(extract_stock_symbols(comment.body))

    return symbols


def rank_symbols(symbols):
    """
    Rank stock symbols by frequency of appearance.

    :param symbols: A list of stock symbols.
    :return: A list of tuples (symbol, count) sorted by frequency.
    """
    return Counter(symbols).most_common()


def main():
    """
    Main function to run the Reddit Ticker Trends scanner.
    """
    reddit = create_reddit_client()
    subreddit = "investing"

    symbols = process_posts_and_comments(subreddit, reddit)
    ranked_symbols = rank_symbols(symbols)

    print("Top 50 most popular stock symbols mentioned:")
    for rank, (symbol, count) in enumerate(ranked_symbols[:50], start=1):
        print(f"{rank}. {symbol} (mentioned {count} times)")


if __name__ == "__main__":
    main()
