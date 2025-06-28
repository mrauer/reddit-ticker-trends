<!-- PROJECT LOGO -->
<p align="center">
  <a href="https://github.com/mrauer/reddit-ticker-trends">
    <img src="logo.png" alt="Logo">
  </a>

  <h3 align="center">Reddit Ticker Trends</h3>

  <p align="center">A Python-based tool that connects to the Reddit API to monitor posts and comments for discussions about ETFs (Exchange-Traded Funds) and stocks. It processes posts and nested comments, identifies potential stock symbols using pattern recognition combined with English word filtering, and ranks the symbols by popularity based on their frequency of mention..
    <br />
    <br />
    <a href="https://github.com/mrauer/reddit-ticker-trends/issues">Report Bug</a>
    ·
    <a href="https://github.com/mrauer/reddit-ticker-trends/issues">Request Feature</a>
  </p>
</p>

## Table of Contents

1. [Motivations](#motivations)  
2. [Configuration](#configuration)  
3. [Installation](#installation)  
4. [How to Use](#how-to-use)  
5. [Sample Output](#sample-output)  
6. [Test Portfolios](#test-portfolios)  

---

## Motivations

This project is an experiment to explore whether selecting stocks or ETFs based on their mention frequency in popular Reddit forums can help identify potentially profitable investment portfolios. The collected data is intended as a resource for insight and further analysis rather than direct investment advice.

---

## Configuration

To run this project, you will need:

- A Reddit developer account with credentials:
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`

Set these as environment variables in your system.

---

## Installation

It is recommended to use a **virtual environment** to avoid dependency conflicts.

### Create and Activate a Virtual Environment

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
````

### Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

Dependencies include:

* `praw` (Reddit API wrapper)
* `yfinance` (financial data)
* `nltk` (natural language processing)
* `certifi` (SSL certificates)

---

## How to Use

Run the tool from the command line with:

```bash
python3 main.py --subreddit investing --limit 100 --num_results 50
```

### Arguments

* `--subreddit`: Subreddit to scan (default: `investing`)
* `--limit`: Number of Reddit posts to process (default: 100)
* `--num_results`: Number of top results to display and classify (default: 50)

---

## Sample Output

```
2025-06-28 14:17:05,843 - INFO - Processed 200 posts, found 23645 raw symbols
2025-06-28 14:17:05,850 - INFO - Ranked total of 3914 unique symbols
2025-06-28 14:17:05,850 - INFO - Classifying 50 symbols...

Top 50 valid Stock/ETF symbols:
1. VOO (ETF) - 756 mentions
2. BTC (ETF) - 654 mentions
3. VTI (ETF) - 614 mentions
4. QQQ (ETF) - 539 mentions
5. AREN (Stock) - 477 mentions
6. VS (Stock) - 419 mentions
7. TQQQ (ETF) - 317 mentions
8. OP (Stock) - 285 mentions
9. VT (ETF) - 257 mentions
10. USD (ETF) - 233 mentions
... (continued) ...
50. DD (Stock) - 54 mentions
2025-06-28 14:17:15,238 - INFO - Analysis complete.
```

---

## Test Portfolios

### Portfolio 1

| Ticker | Current Value (USD) | 1-Year Growth (%) | 5-Year Growth (%) | Post-Experiment Growth (2025–2026) (%) |
| ------ | ------------------- | ----------------- | ----------------- | -------------------------------------- |
| SCHD   | 27.01               | 7.26%             | 41.33%            | TBD                                    |
| TSLA   | 394.74              | 68.09%            | 1,138.83%         | TBD                                    |
| QQQ    | 507.21              | 26.99%            | 135.90%           | TBD                                    |
| VOO    | 533.89              | 24.61%            | 81.16%            | TBD                                    |
| NVDA   | 135.91              | 163.66%           | 2,193.13%         | TBD                                    |
