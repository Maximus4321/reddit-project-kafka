import json
from kafka import KafkaConsumer
from wordcloud import WordCloud
import re
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

subreddit = config.get("reddit_subreddit", "").strip()
keyword = config.get("reddit_keyword", "").strip()

consumer = KafkaConsumer(
    "processed_reddit_posts",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

sentiment_text = defaultdict(list)
sentiments = ['positive', 'negative']

if not os.path.exists("wordclouds"):
    os.makedirs("wordclouds")

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def generate_word_cloud(texts, sentiment):
    if not texts or all(not text.strip() for text in texts):
        print(f"No words available for the '{sentiment}' sentiment. Skipping word cloud generation.")
        return None
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(texts))
    return wordcloud

def combine_word_clouds(wordclouds, subreddit, keyword):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    for ax, sentiment, wordcloud in zip(axes, sentiments, wordclouds):
        if wordcloud:
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            ax.set_title(f"Word Cloud for {sentiment} Sentiment")
        else:
            ax.axis("off")
            ax.set_title(f"No words for {sentiment} Sentiment")
    
    sanitized_subreddit = re.sub(r'[^a-zA-Z0-9]', '_', subreddit) if subreddit else 'all_subreddits'
    sanitized_keyword = re.sub(r'[^a-zA-Z0-9]', '_', keyword) if keyword else 'all_posts'
    
    combined_filename = f"wordclouds/{sanitized_subreddit}_{sanitized_keyword}_combined_wordcloud.png"
    plt.savefig(combined_filename)
    plt.close()
    print(f"Combined word cloud saved as {combined_filename}")

print(f"Waiting for processed Reddit posts from subreddit '{subreddit}' with keyword '{keyword}'...\n")

count = 0
for message in consumer:
    post_data = message.value
    sentiment = post_data["sentiment"]
    post_text = post_data["post"]["title"] + " " + post_data["post"]["selftext"]

    if sentiment in sentiments:
        clean_post = clean_text(post_text)
        sentiment_text[sentiment].append(clean_post)
        count += 1

    if count % 20 == 0:
        if sentiment_text['positive'] and sentiment_text['negative']:
            wordcloud_positive = generate_word_cloud(sentiment_text['positive'], 'positive')
            wordcloud_negative = generate_word_cloud(sentiment_text['negative'], 'negative')
            combine_word_clouds([wordcloud_positive, wordcloud_negative], subreddit, keyword)
        else:
            print("Insufficient data for both sentiments. Skipping word cloud generation.")
