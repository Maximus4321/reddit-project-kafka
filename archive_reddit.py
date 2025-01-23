import json
import os

from kafka import KafkaConsumer

archive_dir = "archive"
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)

positive_file = os.path.join(archive_dir, "positive_posts.json")
negative_file = os.path.join(archive_dir, "negative_posts.json")

consumer = KafkaConsumer(
    "processed_reddit_posts",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

def save_post_to_file(post_data, sentiment_file):
    with open(sentiment_file, "a") as f:
        json.dump(post_data, f)
        f.write("\n")

for message in consumer:
    post_data = message.value
    sentiment = post_data["sentiment"]

    if sentiment == "positive":
        save_post_to_file(post_data, positive_file)
        print(f"Saved positive post: {post_data['post']['title']}")
    elif sentiment == "negative":
        save_post_to_file(post_data, negative_file)
        print(f"Saved negative post: {post_data['post']['title']}")
