<!-- PROJECT LOGO -->
<p align="center">
  <a href="https://github.com/mrauer/reddit-ticker-trends">
    <img src="logo.png" alt="Logo">
  </a>

  <h3 align="center">Reddit Ticker Trends</h3>

  <p align="center">A python-based tool that connects to the Reddit API to monitor posts and comments for discussions about ETFs (Exchange-Traded Funds). It processes posts and nested comments, identifies potential stock symbols using pattern recognition, and ranks the symbols by their popularity based on how frequently they're mentioned.
    <br />
    <br />
    <a href="https://github.com/mrauer/reddit-ticker-trends/issues">Report Bug</a>
    ·
    <a href="https://github.com/mrauer/reddit-ticker-trends/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li><a href="#motivations">Motivations</a></li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#how-to-use">How to Use</a></li>
    <li><a href="#dataset">Dataset</a></li>
    <li><a href="#test-portfolios">Test Portfolios</a></li>
  </ol>

<!-- MOTIVATIONS -->
## Motivations

This is a small experiment to determine whether selecting stocks or ETFs based on their mention frequency in one of the most popular, if not the most popular, forums can result in a portfolio of profitable assets over the long term. The batches listed on this page may or may not hold actual value, but they should provide insight into the potential usefulness of the dataset generated by this software.

<!-- CONFIGURATION -->
## Configuration

Once you have a Reddit developer account, you'll receive a client ID and a client secret. Add these as environment variables in your system using `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`. Additionally, install the `praw` library using pip.

<!-- HOW TO USE -->
## How to Use

Starting with version 1.0.0, simply run `python3 main.py`.

<!-- DATASET -->
## Dataset

This dataset was generated on January 11, 2025, and retrieves the top 50 tickers from 200 subreddits:

| Rank | Ticker/Term | Mentions |
|------|-------------|----------|
| 1    | ETF         | 2922     |
| 2    | VTI         | 710      |
| 3    | VOO         | 706      |
| 4    | SPY         | 508      |
| 5    | BTC         | 469      |
| 6    | QQQ         | 449      |
| 7    | IRA         | 423      |
| 8    | ARK         | 338      |
| 9    | TQQQ        | 257      |
| 10   | VXUS        | 205      |
| 11   | ARKK        | 202      |
| 12   | DCA         | 192      |
| 13   | SCHD        | 188      |
| 14   | GBTC        | 162      |
| 15   | USD         | 152      |
| 16   | TSLA        | 151      |
| 17   | NAV         | 148      |
| 18   | BND         | 142      |
| 19   | SEC         | 142      |
| 20   | WSB         | 124      |
| 21   | VGT         | 114      |
| 22   | HYSA        | 112      |
| 23   | UPRO        | 112      |
| 24   | ICLN        | 109      |
| 25   | NVDA        | 106      |
| 26   | ETH         | 98       |
| 27   | AVUV        | 94       |
| 28   | USA         | 87       |
| 29   | JEPI        | 86       |
| 30   | AUM         | 85       |
| 31   | MSCI        | 83       |
| 32   | QQQM        | 79       |
| 33   | VUG         | 77       |
| 34   | ARKG        | 76       |
| 35   | IMO         | 73       |
| 36   | TMF         | 69       |
| 37   | AAPL        | 65       |
| 38   | GME         | 64       |
| 39   | MSOS        | 63       |
| 40   | MSTR        | 62       |
| 41   | BTCC        | 62       |
| 42   | MSFT        | 61       |
| 43   | TIPS        | 59       |
| 44   | ESG         | 58       |
| 45   | NOT         | 58       |
| 46   | TLT         | 57       |
| 47   | YTD         | 54       |
| 48   | FZROX       | 53       |
| 49   | VTSAX       | 52       |
| 50   | SPX         | 49       |

As you can see, the data for this release isn't perfect, but it provides a foundation to explore some interesting possibilities.

<!-- TEST PORTFOLIOS -->
## Test Portfolios

### Portfolio 1

| Ticker | Current Value (USD) | 1-Year Growth (%) | 5-Year Growth (%) | Post-Experiment Growth (2025–2026) (%) |
|--------|----------------------|-------------------|-------------------|----------------------------------|
| SCHD   | 27.01               | 7.26%            | 41.33%            | TBD                              |
| TSLA   | 394.74              | 68.09%           | 1,138.83%         | TBD                              |
| QQQ    | 507.21              | 26.99%           | 135.90%           | TBD                              |
| VOO    | 533.89              | 24.61%           | 81.16%            | TBD                              |
| NVDA   | 135.91              | 163.66%          | 2,193.13%         | TBD                              |
