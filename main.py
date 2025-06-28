import argparse
import logging
import os
import re
import ssl
from collections import Counter

import certifi
import nltk
import praw
import yfinance as yf
from nltk.corpus import words

# Version
VERSION = "v3.0.0"

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

STATIC_STOPWORDS = {
    "ADDS", "ALGO", "APHA", "AREAS", "ASKED", "ATM", "ATH", "BALLS", "BANKS",
    "BAGS", "BEATS", "BETS", "BIDEN", "BLOG", "BOFA", "BOOKS", "BORED", "BTW",
    "BUCKS", "BUYS", "CALLS", "CARES", "CARDS", "CD", "CDS", "CEO", "CLASSIFY",
    "CNBC", "CO", "COINS", "COM", "CONDO", "COSTS", "CUTS", "DCA", "DEALS",
    "DEMS", "DIDN", "DOESN", "DROPS", "DRUGS", "EMOJI", "ENDS", "ERROR", "ETF",
    "ETFDB", "ETFS", "ETC", "EURO", "EV", "EVS", "FACTS", "FAILED", "FALLS",
    "FEELS", "FEES", "FEWER", "FIRMS", "FLOWS", "FML", "FOMO", "FSD", "FUELS",
    "FUCK", "GAMES", "GBP", "GETS", "GIVES", "GOALS", "GONNA", "GOTTA", "GOV",
    "GROWS", "GUYS", "HADN", "HAHA", "HANDS", "HAS", "HASNT", "HEADS", "HEARD",
    "HELD", "HELPS", "HIGH", "HIGHS", "HITS", "HMM", "HOLDS", "HTML", "HTTP",
    "HTM", "HOURS", "HSA", "HYPE", "IB", "IDEAS", "IMGUR", "IMHO", "IM", "INC",
    "INTEL", "IPO", "IRAS", "ISN", "ISNT", "ISH", "JOBS", "KEEPS", "KINDA",
    "KINDS", "KNOWS", "LAWS", "LEAPS", "LETFS", "LETS", "LIBOR", "LIKED",
    "LIKES", "LINES", "LIVE", "LIVES", "LL", "LMAO", "LOANS", "LOL", "LOSES",
    "LOOKS", "LOWS", "MAKES", "MEANS", "MEGA", "MEME", "MEMES", "MF", "MM",
    "MONEY", "MOVES", "MOVED", "MULTI", "NAH", "NAV", "NBBO", "NAMES", "NFT",
    "NOTES", "NP", "NYSE", "OBAMA", "OKAY", "ONES", "ORG", "OTC", "OWNED",
    "PAID", "PARTS", "PDF", "PE", "PHP", "PICKS", "PLANS", "PLAYS", "PNG",
    "PONZI", "POSTS", "POTX", "POOLS", "PUTIN", "PUTS", "REITS", "RISES",
    "RISKS", "ROLLS", "ROTH", "RULES", "RUNS", "SAYS", "SAFER", "SALES",
    "SEEMS", "SELLS", "SHIT", "SHOWS", "SOCKS", "SP", "SPDR", "SPX", "SQ",
    "STOPS", "SUCKS", "SWAPS", "SAYS", "TALKS", "TAKES", "TAXES", "TDA",
    "TELLS", "TERMS", "TESLA", "THCX", "TOOLS", "TONS", "TYPES", "URL",
    "USA", "USE", "USED", "USES", "USER", "USERS", "USING", "UTC", "UTM",
    "VE", "VOTED", "WANNA", "WARNING", "WARS", "WASN", "WANTS", "WEEKS",
    "WEREN", "WIK", "WIKI", "WINS", "WIPED", "WOODS", "WORDS", "WP", "WWW",
    "YTD", "YOUTU", "YOURE", "YUP"
}

# --- Large English word list from nltk corpus (uppercase) ---
ENGLISH_WORDS = set(word.upper() for word in words.words())


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
    found = re.findall(pattern, text.upper())

    # Filter out words in STATIC_STOPWORDS or ENGLISH_WORDS
    cleaned = [
        s for s in found
        if s not in STATIC_STOPWORDS and s not in ENGLISH_WORDS
    ]
    if cleaned:
        log.debug(f"Extracted symbols (after filtering English words) from text: {cleaned}")
    return cleaned


# --- Reddit Scraping ---
def process_subreddit(reddit, subreddit, limit):
    log.info(f"Processing subreddit: r/{subreddit} | Posts to analyze: {limit}")
    symbols = []
    count = 0

    try:
        for submission in reddit.subreddit(subreddit).search("ETF", limit=limit):
            count += 1
            log.debug(f"Reading post: {submission.title[:80]}")
            symbols += extract_stock_symbols(submission.title)
            symbols += extract_stock_symbols(submission.selftext)

            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                symbols += extract_stock_symbols(comment.body)

    except Exception as e:
        log.error(f"Error accessing subreddit: {e}")

    log.info(f"Processed {count} posts, found {len(symbols)} raw symbols")
    return symbols


# --- Symbol Ranking ---
def rank_symbols(symbols):
    counter = Counter(symbols)
    ranked = counter.most_common()
    log.info(f"Ranked total of {len(ranked)} unique symbols")
    return ranked


# --- Classification using yfinance ---
def classify_symbols(symbols, classify_limit):
    classifications = {}
    log.info(f"Classifying {classify_limit} symbols...")

    for symbol in symbols[:classify_limit]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info or ticker.info
            qt = info.get("quoteType", info.get("type", "")).lower()

            if "etf" in qt:
                cls = "ETF"
            elif "equity" in qt or qt == "stock":
                cls = "Stock"
            else:
                cls = "Unknown"

            log.debug(f"{symbol}: classified as {cls} (quoteType: {qt})")
        except Exception as e:
            cls = "Unknown"
            log.warning(f"Failed to classify {symbol}: {e}")

        classifications[symbol] = cls

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

    classify_limit = args.num_results  # classify only top num_results, not hardcoded 100
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
