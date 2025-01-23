import json
import praw
import time
from kafka import KafkaProducer

with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

reddit_keyword = config.get("reddit_keyword", "").strip()
reddit_subreddit = config.get("reddit_subreddit", "").strip()
client_id = config.get("reddit_client_id", "")
client_secret = config.get("reddit_client_secret", "")
user_agent = config.get("reddit_user_agent", "")

reddit = praw.Reddit(client_id=client_id, 
                     client_secret=client_secret, 
                     user_agent=user_agent)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf8"),
)

i = 0
last_post_name = None
max_posts = 1000

while i < max_posts:
    try:
        search_results = []
        if reddit_subreddit:
            print(f"Searching posts in subreddit: {reddit_subreddit} with keyword '{reddit_keyword}'")
            if reddit_keyword:
                search_results = reddit.subreddit(reddit_subreddit).search(
                    reddit_keyword, limit=1000, sort='new', time_filter='all', params={"after": last_post_name})
            else:
                search_results = reddit.subreddit(reddit_subreddit).new(limit=1000, params={"after": last_post_name})
        else:
            print(f"Searching all of Reddit for keyword '{reddit_keyword}'")
            if reddit_keyword:
                search_results = reddit.subreddit("all").search(
                    reddit_keyword, limit=1000, sort='new', time_filter='all', params={"after": last_post_name})
            else:
                search_results = reddit.subreddit("all").new(limit=1000, params={"after": last_post_name})

        new_posts_found = False
        for post in search_results:
            if i >= max_posts:
                break
            new_posts_found = True
            post_data = {
                "title": post.title,
                "id": post.id,
                "created_utc": post.created_utc,
                "selftext": post.selftext,
                "subreddit": post.subreddit.display_name
            }
            print(f"Post found: {post.title}")
            producer.send("raw_reddit_posts", value=post_data)
            i += 1
            print(f"Sent post {i} to Kafka topic 'raw_reddit_posts'")
            last_post_name = post.name

        if not new_posts_found:
            print("No new posts found. Exiting.")
            break

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)

print("Reached the set limit of 1000 posts. Exiting.")
