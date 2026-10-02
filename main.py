import argparse
import json
import logging
import os
import re
import ssl
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import certifi
import nltk
import praw
import yfinance as yf
from nltk.corpus import words

# Version
VERSION = "v4.0.0"

# Fix certificate verification issue for nltk downloads
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# Download nltk 'words' corpus if not already present
try:
    words.words()
except LookupError:
    nltk.download('words')

# --- Logging Setup ---
log = logging.getLogger()
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('reddit_ticker_trends.log', mode='w')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
log.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
log.addHandler(console_handler)

# yfinance logs expected lookup failures (invalid/delisted symbols) at ERROR level;
# we already catch and log these ourselves in classify_symbol, so quiet its logger.
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# --- Large English word list from nltk corpus (uppercase) ---
ENGLISH_WORDS = set(word.upper() for word in words.words())

# --- Ticker classification cache ---
# Classifying a symbol via yfinance is the authoritative check for "is this a
# real ticker" (not a hardcoded guess), so we cache every result (including
# "Unknown") on disk and never pay for the same lookup twice. This also means
# junk acronyms get permanently filtered out after the first time they're seen,
# without anyone having to hand-maintain a stopword list.
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ticker_cache.json')


def load_ticker_cache():
    try:
        with open(CACHE_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_ticker_cache(cache):
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2, sort_keys=True)


# Real, tradable tickers that are also common English words/abbreviations, so
# yfinance's validity check can't tell them apart from ordinary usage. Unlike
# the old stopword list, this isn't guessing at junk (the cache handles that
# automatically) - every entry here is a confirmed real ticker kept out on
# purpose. Extend only when a genuine word/ticker collision like this is found.
AMBIGUOUS_WORD_TICKERS = {"USA", "UK", "CD", "IPO", "TIPS"}


# --- Reddit Client Setup ---
def create_reddit_client():
    log.info("Creating Reddit client...")
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=f'Reddit Ticker Trends {VERSION} English Words Filter'
    )


# --- Symbol Extraction ---
def extract_stock_symbols(text):
    if not text:
        return []
    pattern = r'\b[A-Z]{2,5}\b'  # 2 to 5 uppercase letters, typical ticker length
    found = re.findall(pattern, text)  # match existing case only; avoids false positives from lowercase words

    # Filter out real English words; remaining junk acronyms (WSB, VIX, etc.)
    # get caught later by live ticker classification instead of a static list.
    cleaned = [
        s for s in found
        if s not in ENGLISH_WORDS and s not in AMBIGUOUS_WORD_TICKERS
    ]
    if cleaned:
        log.debug(f"Extracted symbols (after filtering English words) from text: {cleaned}")
    return cleaned


# --- Reddit Scraping ---
def process_submission(submission):
    try:
        log.debug(f"Reading post: {submission.title[:80]}")
        symbols = extract_stock_symbols(submission.title)
        symbols += extract_stock_symbols(submission.selftext)

        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            symbols += extract_stock_symbols(comment.body)
        return symbols
    except Exception as e:
        log.error(f"Error processing post {submission.id}: {e}")
        return []


def process_subreddit(reddit, subreddit, limit, max_workers=8):
    log.info(f"Processing subreddit: r/{subreddit} | Posts to analyze: {limit}")
    symbols = []

    try:
        submissions = list(reddit.subreddit(subreddit).search("ETF", limit=limit))
    except Exception as e:
        log.error(f"Error accessing subreddit: {e}")
        return symbols

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for result in executor.map(process_submission, submissions):
            symbols += result

    log.info(f"Processed {len(submissions)} posts, found {len(symbols)} raw symbols")
    return symbols


# --- Symbol Ranking ---
def rank_symbols(symbols):
    counter = Counter(symbols)
    ranked = counter.most_common()
    log.info(f"Ranked total of {len(ranked)} unique symbols")
    return ranked


# Below this daily share volume, a symbol is too obscure/illiquid to plausibly
# be what's actually being discussed - catches real-but-irrelevant collisions
# like ticker CAGR (an obscure micro-cap) vs. the acronym "CAGR" (compound
# annual growth rate), without having to know about each one in advance.
MIN_DAILY_VOLUME = 10_000


# --- Classification using yfinance ---
def classify_symbol(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info or ticker.info
        qt = info.get("quoteType", info.get("type", "")).lower()
        volume = info.get("lastVolume") or 0

        if volume < MIN_DAILY_VOLUME:
            cls = "Unknown"
        elif "etf" in qt:
            cls = "ETF"
        elif "equity" in qt or qt == "stock":
            cls = "Stock"
        else:
            cls = "Unknown"

        log.debug(f"{symbol}: classified as {cls} (quoteType: {qt}, volume: {volume})")
    except Exception as e:
        cls = "Unknown"
        log.warning(f"Failed to classify {symbol}: {e}")

    return symbol, cls


def classify_symbols(symbols, classify_limit, max_workers=10):
    cache = load_ticker_cache()
    to_classify = symbols[:classify_limit]

    classifications = {s: cache[s] for s in to_classify if s in cache}
    uncached = [s for s in to_classify if s not in cache]

    log.info(f"Classifying {len(uncached)} symbols ({len(classifications)} from cache)...")

    if uncached:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for symbol, cls in executor.map(classify_symbol, uncached):
                classifications[symbol] = cls
                cache[symbol] = cls
        save_ticker_cache(cache)

    return classifications


# --- Main Entry ---
def main():
    parser = argparse.ArgumentParser(description=f"Reddit Ticker Trends {VERSION} with English Words Filtering")
    parser.add_argument('--limit', type=int, default=100, help='Number of Reddit posts to scan')
    parser.add_argument('--num_results', type=int, default=50, help='Top N symbols to return and classify')
    parser.add_argument('--subreddit', type=str, default='investing', help='Subreddit to scan')
    args = parser.parse_args()

    log.info(f"Starting Reddit Ticker Trend {VERSION} with English words filtering...")

    reddit = create_reddit_client()
    symbols = process_subreddit(reddit, args.subreddit, args.limit)

    if not symbols:
        print("No symbols found. Try increasing the post limit or changing subreddit.")
        log.warning("No symbols extracted.")
        return

    ranked_all = rank_symbols(symbols)

    # Classify more candidates than num_results: without a stopword list, some
    # non-ticker acronyms (not in the English dictionary) still rank highly and
    # get discarded after classification, so we need headroom to still surface
    # num_results valid Stock/ETF symbols.
    classify_limit = min(len(ranked_all), args.num_results * 3)
    top_candidates = [s for s, _ in ranked_all[:classify_limit]]

    classifications = classify_symbols(top_candidates, classify_limit)

    # Filter ranked list by classified types Stock or ETF
    ranked_filtered = [(s, c) for s, c in ranked_all if classifications.get(s) in ("Stock", "ETF")]

    if not ranked_filtered:
        print("No valid Stock or ETF tickers found.")
        log.warning("All classified symbols were Unknown or filtered.")
        return

    print(f"\nTop {args.num_results} valid Stock/ETF symbols:")
    for i, (symbol, count) in enumerate(ranked_filtered[:args.num_results], 1):
        cls = classifications.get(symbol, "Unknown")
        print(f"{i}. {symbol} ({cls}) - {count} mentions")

    log.info("Analysis complete.")


if __name__ == "__main__":
    main()
