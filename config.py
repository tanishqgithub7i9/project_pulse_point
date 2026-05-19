"""
config.py — Project Pulse-Point Configuration
==============================================
WHY THIS FILE EXISTS:
    Instead of scattering settings (API keys, file paths, intervals) 
    across every file, we keep them ALL in one place.
    This is a professional best practice — if you need to change the
    database path or refresh rate, you change it ONCE here.
"""

# ─── Database ─────────────────────────────────────────────────────────────────
DB_PATH = 'pulse_point.db'          # SQLite database file path

# ─── External APIs ────────────────────────────────────────────────────────────
# CoinGecko: Free Bitcoin price API. No API key required!
COINGECKO_URL = (
    'https://api.coingecko.com/api/v3/simple/price'
    '?ids=bitcoin&vs_currencies=usd'
)

# RSS News Feeds: Free, real-time crypto news. No API key required!
# RSS is a standard format that news sites publish for automated reading.
RSS_FEEDS = [
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'https://cointelegraph.com/rss',
    'https://cryptoslate.com/feed/',
]

# ─── Pipeline Settings ────────────────────────────────────────────────────────
REFRESH_INTERVAL = 300              # Seconds between each data fetch (5 min)

# ─── Sentiment Classification Thresholds ──────────────────────────────────────
# TextBlob scores range from -1.0 (very negative) to +1.0 (very positive)
# We add a small buffer around 0 to avoid false signals
BULLISH_THRESHOLD =  0.05           # Sentiment above this → BULLISH 🟢
BEARISH_THRESHOLD = -0.05           # Sentiment below this → BEARISH 🔴
