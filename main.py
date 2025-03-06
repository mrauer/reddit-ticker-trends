import os
import praw
import re
import argparse
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


def process_posts_and_comments(subreddit, reddit, limit):
    """
    Extract stock symbols from posts and comments in a subreddit.

    :param subreddit: The name of the subreddit to process.
    :param reddit: The authenticated Reddit client instance.
    :param limit: The number of posts to process.
    :return: A list of stock symbols mentioned in posts and comments.
    """
    symbols = []

    for submission in reddit.subreddit(subreddit).search("ETF", limit=limit):
        symbols.extend(extract_stock_symbols(submission.title))
        symbols.extend(extract_stock_symbols(submission.selftext))

        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            symbols.extend(extract_stock_symbols(comment.body))

    return symbols


def rank_symbols(symbols, num_results):
    """
    Rank stock symbols by frequency of appearance.

    :param symbols: A list of stock symbols.
    :param num_results: The number of results to return.
    :return: A list of tuples (symbol, count) sorted by frequency.
    """
    return Counter(symbols).most_common(num_results)


def main():
    """
    Main function to run the Reddit Ticker Trends scanner.
    """
    parser = argparse.ArgumentParser(description="Reddit Ticker Trends - Stock Symbol Trend Analyzer")
    parser.add_argument('--limit', type=int, default=100, help='Number of posts to process (default: 100)')
    parser.add_argument('--num_results', type=int, default=50, help='Number of top results to display (default: 50)')
    parser.add_argument('--subreddit', type=str, default='investing', help='Subreddit to analyze (default: investing)')

    args = parser.parse_args()

    reddit = create_reddit_client()
    symbols = process_posts_and_comments(args.subreddit, reddit, args.limit)
    ranked_symbols = rank_symbols(symbols, args.num_results)

    print(f"Top {args.num_results} most popular stock symbols mentioned:")
    for rank, (symbol, count) in enumerate(ranked_symbols, start=1):
        print(f"{rank}. {symbol} (mentioned {count} times)")


if __name__ == "__main__":
    main()
