from textblob import TextBlob

# These represent comments you might find on X (Twitter) or Reddit
comments = [
    "Bitcoin is amazing! I'm so happy I bought it, to the moon! 🚀", # Positive
    "This is a total disaster. I lost everything and I'm very angry.", # Negative
    "Today is Thursday and Bitcoin is a type of cryptocurrency.",   # Neutral
]

print("--- Sentiment Analysis Test ---")

for comment in comments:
    # TextBlob reads the sentence
    blob = TextBlob(comment)
    
    # Polarity is a score from -1.0 (Very Sad) to +1.0 (Very Happy)
    score = blob.sentiment.polarity
    
    # Let's make it easy to read
    if score > 0:
        feeling = "POSITIVE 😊"
    elif score < 0:
        feeling = "NEGATIVE 😡"
    else:
        feeling = "NEUTRAL 😐"
    
    print(f"Comment: {comment}")
    print(f"Score: {score} | Verdict: {feeling}")
    print("-" * 30)