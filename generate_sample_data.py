"""
generate_sample_data.py — Pulse-Point Historical Data Seeder
=============================================================
WHAT THIS DOES:
    Generates 7 days of realistic Bitcoin price + sentiment data
    and inserts it into the database.

WHY WE NEED THIS:
    The tracker.py collects 1 data point every 5 minutes.
    To get 7 days of data, you'd need to wait 7 days!
    Instead, we SIMULATE realistic historical data so we have
    something meaningful to analyze RIGHT NOW.

THE MATHS (Geometric Brownian Motion - GBM):
    This is the same model used in quantitative finance to simulate
    stock/crypto prices. A random walk where:
    - 'mu' = average daily drift (upward or downward trend)
    - 'sigma' = volatility (how much it moves each step)
    
    Price(t+1) = Price(t) * (1 + random_shock)
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta
import config
from database_setup_v2 import setup_database


# ── Realistic Bitcoin Headlines ────────────────────────────────────────────────
# Varied headlines that simulate what you'd actually get from news feeds
# Each has a different implied sentiment — some bullish, some bearish, some neutral

BULLISH_HEADLINES = [
    'Bitcoin bulls eye new all-time high as institutional demand soars',
    'Crypto markets surge amid positive regulatory developments globally',
    'Bitcoin hash rate hits new all-time high, network security increases',
    'Major asset manager adds Bitcoin to portfolio, sparking rally',
    'Bitcoin halving event boosts miner confidence and market optimism',
    'Retail and institutional Bitcoin buying hits record weekly volumes',
    'Bitcoin shows strong resistance levels as bullish momentum builds',
]

NEUTRAL_HEADLINES = [
    'Bitcoin consolidates near key support, analysts watch next move',
    'Crypto market shows mixed signals as traders await macro data',
    'Bitcoin trading volume stabilizes after recent weekly movement',
    'Analysts remain divided on Bitcoin short-term price direction',
    'Bitcoin price holds steady ahead of Federal Reserve decision',
    'Crypto market cap unchanged as Bitcoin dominance stays flat',
]

BEARISH_HEADLINES = [
    'Bitcoin drops amid profit-taking as overbought indicators flash',
    'Crypto sell-off continues as macroeconomic uncertainty weighs',
    'Bitcoin volatility spikes higher as traders reduce risk exposure',
    'Market correction deepens: Bitcoin tests key support at lower levels',
    'Regulatory crackdown fears send Bitcoin lower in Asian trading',
    'Bitcoin miners reduce holdings as energy costs rise significantly',
]


def generate_price_series(start_price: float, n_points: int,
                          mu: float = 0.0001, sigma: float = 0.007) -> list:
    """
    Generate a price series using Geometric Brownian Motion.
    
    Args:
        start_price: Starting Bitcoin price in USD
        n_points: Number of data points to generate
        mu: Drift (positive = upward trend, negative = downward)
        sigma: Volatility (higher = bigger swings)
    
    Returns:
        List of prices
    """
    np.random.seed(42)  # Fixed seed = reproducible results (great for demos!)
    prices = [start_price]

    for _ in range(n_points - 1):
        # Each step: multiply by a random factor centered near 1.0
        # np.random.normal(mu, sigma) gives a random number from a bell curve
        shock = np.random.normal(mu, sigma)
        new_price = prices[-1] * (1 + shock)
        prices.append(round(new_price, 2))

    return prices


def generate_sentiment_series(prices: list, noise_level: float = 0.25) -> list:
    """
    Generate sentiment scores that PARTIALLY correlate with price movements.
    
    In real markets, news sentiment and price don't move perfectly together.
    We add random noise to make it realistic.
    """
    np.random.seed(123)

    # Calculate % price returns
    price_arr = np.array(prices)
    returns = np.diff(price_arr, prepend=price_arr[0]) / np.maximum(price_arr, 1)

    # Scale returns to sentiment range, then add noise
    base_sentiment = returns * 40               # Scale factor
    noise = np.random.normal(0, noise_level, len(prices))
    raw_sentiment = base_sentiment + noise

    # Clip to valid range [-1.0, +1.0]
    sentiment = np.clip(raw_sentiment, -1.0, 1.0)
    return [round(float(s), 4) for s in sentiment]


def pick_headline(sentiment_score: float) -> str:
    """Pick a contextually appropriate headline based on sentiment."""
    import random
    random.seed(int(abs(sentiment_score) * 1000))

    if sentiment_score > config.BULLISH_THRESHOLD:
        return random.choice(BULLISH_HEADLINES)
    elif sentiment_score < config.BEARISH_THRESHOLD:
        return random.choice(BEARISH_HEADLINES)
    else:
        return random.choice(NEUTRAL_HEADLINES)


def seed_database(days: int = 7, interval_minutes: int = 30):
    """
    Main function: generate data and insert into database.
    
    Args:
        days: How many days of historical data to create
        interval_minutes: Time gap between each data point
    """

    # ── Ensure database and schema exist first ─────────────────────────────────
    setup_database()

    # ── Generate timestamps ────────────────────────────────────────────────────
    n_points = int(days * 24 * 60 / interval_minutes)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    timestamps = [
        (start_time + timedelta(minutes=i * interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')
        for i in range(n_points)
    ]

    # ── Generate price and sentiment data ──────────────────────────────────────
    start_price = 83_500.00    # Realistic BTC price (April 2026)
    prices = generate_price_series(start_price, n_points)
    sentiments = generate_sentiment_series(prices)
    headlines = [pick_headline(s) for s in sentiments]

    # ── Insert into database ───────────────────────────────────────────────────
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # Clear existing data before re-seeding
    cursor.execute('SELECT COUNT(*) FROM bitcoin_prices')
    existing = cursor.fetchone()[0]
    if existing > 0:
        print(f'⚠️  Clearing {existing:,} existing rows and re-seeding...')
        cursor.execute('DELETE FROM bitcoin_prices')

    # Batch insert (much faster than one-by-one!)
    cursor.executemany(
        'INSERT INTO bitcoin_prices (timestamp, price, sentiment, headline) VALUES (?, ?, ?, ?)',
        list(zip(timestamps, prices, sentiments, headlines))
    )

    conn.commit()
    conn.close()

    # ── Print summary ──────────────────────────────────────────────────────────
    print()
    print('═' * 55)
    print('  ✅ DATABASE SEEDED SUCCESSFULLY!')
    print('═' * 55)
    print(f'  Data points   : {n_points:,} observations')
    print(f'  Date range    : {timestamps[0][:10]} → {timestamps[-1][:10]}')
    print(f'  Price range   : ${min(prices):>10,.2f} — ${max(prices):>10,.2f}')
    print(f'  Avg price     : ${sum(prices)/len(prices):>10,.2f}')
    print(f'  Avg sentiment : {sum(sentiments)/len(sentiments):>10.4f}')
    print('═' * 55)
    print()
    print('  Next steps:')
    print('  1. python create_notebook.py   → Generate analysis notebook')
    print('  2. streamlit run dashboard.py  → Launch live dashboard')
    print()


if __name__ == '__main__':
    seed_database()
