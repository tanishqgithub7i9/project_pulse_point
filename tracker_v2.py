"""
tracker_v2.py — Project Pulse-Point v2.0 Live Data Pipeline
============================================================
MAJOR IMPROVEMENTS OVER tracker.py:
    ❌ OLD: Hardcoded comment "Bitcoin looks very strong today!" (fake!)
    ✅ NEW: Fetches REAL headlines from CoinDesk, CoinTelegraph RSS feeds
    
    ❌ OLD: Sentiment never changed (always same fake sentence)
    ✅ NEW: Analyzes 5-15 DIFFERENT headlines per cycle — score changes!

    ❌ OLD: print() statements only — no record of what happened
    ✅ NEW: Professional logging to both screen AND pipeline.log file

    ❌ OLD: No error handling — one bad API response crashes everything
    ✅ NEW: Graceful error handling with retries and continue logic

HOW TO RUN:
    python tracker_v2.py
    Press Ctrl+C to stop safely.
    
    Data is saved to pulse_point.db every 5 minutes.
"""

import requests
import time
import sqlite3
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Tuple

from textblob import TextBlob
import config


# ─── LOGGING SETUP ────────────────────────────────────────────────────────────
# WHAT IS LOGGING?
#   Logging is the professional replacement for print().
#   It automatically adds timestamps, log levels (INFO/WARNING/ERROR),
#   and saves to a FILE so you can review what happened later.
#   Every production data pipeline uses logging.

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('pipeline.log', encoding='utf-8'),  # Saves to file
        logging.StreamHandler()                                   # Also prints to screen
    ]
)
logger = logging.getLogger(__name__)


# ─── FUNCTION 1: Fetch News Headlines from RSS ────────────────────────────────
def fetch_rss_headlines(feed_url: str, max_items: int = 5) -> list:
    """
    Fetch news headlines from an RSS feed.
    
    WHAT IS RSS?
        RSS (Really Simple Syndication) is an XML format that news sites
        publish automatically. We read it like a constantly-updated newspaper.
        CoinDesk, CoinTelegraph, etc. all provide free RSS feeds.
    
    Args:
        feed_url:  URL of the RSS feed
        max_items: How many headlines to fetch from this feed
    
    Returns:
        List of headline strings (empty list if fetch failed)
    """
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; PulsePointBot/2.0)'}

    try:
        response = requests.get(feed_url, timeout=10, headers=headers)
        response.raise_for_status()      # Raise error for 4xx/5xx HTTP codes

        # Parse the XML response
        root = ET.fromstring(response.content)
        channel = root.find('channel')
        if channel is None:
            return []

        # Extract headline text from each <item><title> element
        items = channel.findall('item')[:max_items]
        headlines = []
        for item in items:
            title_elem = item.find('title')
            if title_elem is not None and title_elem.text:
                headlines.append(title_elem.text.strip())

        return headlines

    except requests.exceptions.Timeout:
        logger.warning(f'⏱️  Timeout fetching: {feed_url}')
        return []
    except requests.exceptions.RequestException as e:
        logger.warning(f'🌐 Network error: {e}')
        return []
    except ET.ParseError as e:
        logger.warning(f'📄 XML parse error: {e}')
        return []


# ─── FUNCTION 2: Get Sentiment from Real Headlines ────────────────────────────
def get_crypto_sentiment() -> Tuple[float, str]:
    """
    Pull real crypto news and calculate average sentiment score.
    
    HOW IT WORKS:
        1. Fetch headlines from each RSS feed in config.RSS_FEEDS
        2. Filter for crypto-relevant headlines (bitcoin, btc, etc.)
        3. Run TextBlob sentiment analysis on each headline
        4. Average all scores → single sentiment number
    
    Returns:
        avg_sentiment (float): Score from -1.0 (bearish) to +1.0 (bullish)
        top_headline  (str):   The most relevant headline (for storage)
    """
    all_headlines = []

    # Collect headlines from all configured RSS feeds
    for feed_url in config.RSS_FEEDS:
        headlines = fetch_rss_headlines(feed_url, max_items=5)
        all_headlines.extend(headlines)
        logger.debug(f'Got {len(headlines)} headlines from {feed_url}')

    if not all_headlines:
        logger.warning('📰 No headlines found — defaulting to neutral sentiment')
        return 0.0, 'No headlines available (check internet connection)'

    # Filter for crypto-relevant headlines to reduce noise
    crypto_keywords = {'bitcoin', 'btc', 'crypto', 'blockchain',
                       'market', 'bull', 'bear', 'halving', 'ethereum'}
    relevant = [h for h in all_headlines
                if any(kw in h.lower() for kw in crypto_keywords)]

    # Use relevant headlines if found, else use all
    headlines_to_analyze = relevant if relevant else all_headlines

    # Run TextBlob sentiment on EACH headline, then average
    # THIS IS THE KEY FIX: real headlines → different score each time!
    sentiments = [TextBlob(h).sentiment.polarity for h in headlines_to_analyze]
    avg_sentiment = sum(sentiments) / len(sentiments)
    top_headline = headlines_to_analyze[0]

    logger.info(
        f'📰 Analyzed {len(headlines_to_analyze)} headlines | '
        f'Sentiment: {avg_sentiment:+.4f} | '
        f'Relevant: {len(relevant)}/{len(all_headlines)}'
    )

    return round(avg_sentiment, 4), top_headline


# ─── FUNCTION 3: Get Bitcoin Price from CoinGecko ────────────────────────────
def get_bitcoin_price() -> Optional[float]:
    """
    Fetch current Bitcoin price from CoinGecko API.
    No API key needed — CoinGecko has a free public endpoint.
    
    Returns:
        price (float): BTC price in USD, or None if request failed
    """
    try:
        response = requests.get(config.COINGECKO_URL, timeout=10)
        response.raise_for_status()
        price = response.json()['bitcoin']['usd']
        return float(price)

    except requests.exceptions.Timeout:
        logger.error('⏱️  Timeout fetching Bitcoin price')
        return None
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        logger.error(f'💸 Price fetch failed: {e}')
        return None


# ─── FUNCTION 4: Save Data Point to Database ─────────────────────────────────
def save_to_db(timestamp: str, price: float,
               sentiment: float, headline: str) -> bool:
    """
    Save one observation to the SQLite database.
    
    Returns:
        bool: True if saved successfully, False on database error
    """
    try:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bitcoin_prices (timestamp, price, sentiment, headline) '
            'VALUES (?, ?, ?, ?)',
            (timestamp, price, sentiment, headline)
        )
        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        logger.error(f'🗄️  Database error: {e}')
        return False


# ─── MAIN PIPELINE LOOP ───────────────────────────────────────────────────────
def run_pipeline():
    """
    Main loop: fetch → analyze → store → wait → repeat.
    
    This is the core of our ETL (Extract, Transform, Load) pipeline:
        Extract:   Pull price and news data from external sources
        Transform: Run sentiment analysis, add timestamp
        Load:      Save the processed data to SQLite
    """
    logger.info('=' * 62)
    logger.info('  PROJECT PULSE-POINT v2.0 — LIVE ETL PIPELINE STARTED')
    logger.info(f'  Saving to       : {config.DB_PATH}')
    logger.info(f'  Refresh rate    : every {config.REFRESH_INTERVAL // 60} minutes')
    logger.info(f'  News sources    : {len(config.RSS_FEEDS)} RSS feeds')
    logger.info('  Press Ctrl+C to stop the pipeline safely.')
    logger.info('=' * 62)

    cycle = 0

    try:
        while True:
            cycle += 1
            logger.info(f'')
            logger.info(f'─── Cycle #{cycle:04d} ──────────────────────────────────')

            # STEP 1: Fetch Bitcoin Price
            price = get_bitcoin_price()
            if price is None:
                logger.warning('Skipping cycle — will retry in 60 seconds.')
                time.sleep(60)
                continue

            logger.info(f'💰 BTC Price: ${price:>10,.2f}')

            # STEP 2: Fetch Real News + Calculate Sentiment
            sentiment, headline = get_crypto_sentiment()

            # STEP 3: Save to Database
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            success = save_to_db(timestamp, price, sentiment, headline)

            if success:
                mood_icon = '🟢' if sentiment > config.BULLISH_THRESHOLD else \
                            '🔴' if sentiment < config.BEARISH_THRESHOLD else '🟡'
                logger.info(
                    f'{mood_icon} SAVED  | Sentiment: {sentiment:+.4f} | '
                    f'Headline: {headline[:50]}...'
                )
            else:
                logger.error('❌ Failed to save data point to database!')

            # STEP 4: Wait for next cycle
            logger.info(f'⏳ Next fetch in {config.REFRESH_INTERVAL // 60} minutes...')
            time.sleep(config.REFRESH_INTERVAL)

    except KeyboardInterrupt:
        logger.info('')
        logger.info('=' * 62)
        logger.info('  ✅ Pipeline stopped safely by user (Ctrl+C).')
        logger.info('  Your data is saved in pulse_point.db')
        logger.info('  Run: jupyter notebook analysis.ipynb  to analyze it!')
        logger.info('  Run: streamlit run dashboard.py        to visualize it!')
        logger.info('=' * 62)


if __name__ == '__main__':
    run_pipeline()
