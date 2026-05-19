import requests
import time
import sqlite3
from textblob import TextBlob

def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        price = response.json()['bitcoin']['usd']
        
        # SIMULATION: In a real project, we'd pull from Twitter/Reddit API here
        # For this step, let's pretend we found this comment online:
        sample_comment = "Bitcoin looks very strong today, I am feeling bullish!"
        
        # Calculate sentiment of that comment
        sentiment_score = TextBlob(sample_comment).sentiment.polarity
        
        return price, sentiment_score
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def save_to_db(timestamp, price, sentiment):
    conn = sqlite3.connect('pulse_point.db')
    cursor = conn.cursor()
    # Updated to include sentiment
    cursor.execute("INSERT INTO bitcoin_prices (timestamp, price, sentiment) VALUES (?, ?, ?)", 
                   (timestamp, price, sentiment))
    conn.commit()
    conn.close()

print("--- PROJECT PULSE-POINT: FULL PIPELINE ACTIVE ---")

try:
    while True:
        price, sentiment = get_crypto_data()
        if price is not None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            save_to_db(timestamp, price, sentiment)
            print(f"[{timestamp}] Price: ${price} | Sentiment: {sentiment}")
        
        time.sleep(30)
except KeyboardInterrupt:
    print("\nPipeline stopped safely.")