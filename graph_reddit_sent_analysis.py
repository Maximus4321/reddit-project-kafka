import json
from kafka import KafkaConsumer
import matplotlib.pyplot as plt
import re
import os

consumer = KafkaConsumer(
    "processed_reddit_posts",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

sentiment_counts = {
    "positive": 0,
    "negative": 0,
}

with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

keyword = config.get("reddit_keyword", "").strip()
subreddit = config.get("reddit_subreddit", "").strip()

def update_sentiment_counts(sentiment):
    if sentiment in sentiment_counts:
        sentiment_counts[sentiment] += 1

processed_count = 0
update_interval = 10

while True:
    for message in consumer:
        post_data = message.value
        post = post_data["post"]
        sentiment = post_data["sentiment"]

        if not keyword or keyword.lower() in post["title"].lower() or keyword.lower() in post["selftext"].lower():
            update_sentiment_counts(sentiment)
            processed_count += 1
            print(f"Processed {processed_count} sentiments: {sentiment_counts}")

            if processed_count % update_interval == 0:
                print(f"Saving graph after {processed_count} sentiments.")
                plt.bar(sentiment_counts.keys(), sentiment_counts.values(), color=['green', 'red'])
                title = f"Sentiment Analysis {'for ' + keyword if keyword else 'on Posts'} {'in ' + subreddit if subreddit else ''}"
                plt.title(title)
                plt.xlabel("Sentiment")
                plt.ylabel("Number of Posts")
                sanitized_keyword = re.sub(r'[^a-zA-Z0-9]', '_', keyword) if keyword else 'all_posts'
                sanitized_subreddit = re.sub(r'[^a-zA-Z0-9]', '_', subreddit) if subreddit else 'all_subreddits'
                plt.savefig(f'graphs/sentiment_graph_{sanitized_subreddit}_{sanitized_keyword}.png')
                plt.close()
