import json
import joblib
import re
from kafka import KafkaConsumer, KafkaProducer
import pandas as pd
import os

with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

uncertainty_threshold = config.get("uncertainty_threshold")

model = joblib.load('config/sentiment_model.pkl')
vectorizer = joblib.load('config/vectorizer.pkl')

consumer = KafkaConsumer(
    "raw_reddit_posts",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf8"),
)

user_feedback_file = 'config/userfeedback.csv'

print("Waiting for Reddit Posts... \n")

def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

def classify_sentiment(text):
    processed_text = preprocess_text(text)
    vectorized_text = vectorizer.transform([processed_text])
    prediction = model.predict_proba(vectorized_text)
    sentiment = model.predict(vectorized_text)[0]
    uncertainty = abs(prediction[0][0] - 0.5)
    return sentiment, uncertainty

def save_feedback(post, sentiment):
    feedback = {
        "id": post["id"],
        "text": post["title"] + " " + post["selftext"],
        "sentiment": sentiment
    }
    df = pd.DataFrame([feedback])
    
    if not os.path.exists(user_feedback_file) or os.path.getsize(user_feedback_file) == 0:
        df.to_csv(user_feedback_file, mode='a', header=True, index=False)
    else:
        df.to_csv(user_feedback_file, mode='a', header=False, index=False)

for message in consumer:
    post = message.value
    full_text = post["title"] + " " + post["selftext"]
    
    sentiment, uncertainty = classify_sentiment(full_text)
    
    if uncertainty < uncertainty_threshold:
        print(f"Post: {post['title']}, Model Sentiment: {sentiment}, Uncertain: {uncertainty}")
        
        if uncertainty_threshold > 0:
            user_input = input(f"The model predicted '{sentiment}'. Do you agree? (Y/N): ").strip().upper()
            
            if user_input == 'N':
                sentiment = "positive" if sentiment == "negative" else "negative"
                save_feedback(post, sentiment)
            else:
                save_feedback(post, sentiment)
        else:
            save_feedback(post, sentiment)
        
    print(f"Post: {post['title']}, Sentiment: {sentiment}")
    
    producer.send("processed_reddit_posts", value={"post": post, "sentiment": sentiment})
