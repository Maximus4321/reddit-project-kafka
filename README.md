Sentiment Analysis Pipeline with Kafka

This repository contains a real-time sentiment analysis pipeline that processes Reddit posts, performs sentiment classification using a machine learning model, visualizes the results, and incorporates user feedback to improve the model.

Setup Instructions
1. Clone the Repository

git clone https://github.com/your-username/sentiment-analysis-kafka.git
cd sentiment-analysis-kafka

2. Sign Up for a Reddit Developer Account

To use the Reddit API, create a developer account and generate credentials:

    Go to Reddit Developer Portal here : https://www.reddit.com/prefs/apps.
    Log in with your Reddit account.
    Click on "Create App" and select "Script".
    Note down the Client ID, Client Secret, and User Agent.

3. Configure the config.json File

Update the config.json file with your Reddit credentials and desired pipeline settings:

```console
{
    "reddit_keyword": "",
    "reddit_subreddit": "",
    "uncertainty_threshold": 0,
    "reddit_client_id": "your_client_id",
    "reddit_client_secret": "your_client_secret",
    "reddit_user_agent": "your_user_agent"
}
```

4. Unzip the sentiment140.zip File

Due to GitHub file size limitations, the Sentiment140 dataset is compressed. Unzip it:

```console
unzip sentiment140.zip -d config/
```

5. Install Dependencies

Install the required Python packages using pip. You can use the provided requirements.txt file:

```console
pip install -r requirements.txt
```

6. Set Up Kafka Topics

Create the necessary Kafka topics:

```console
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Server
bin/kafka-server-start.sh config/server.properties

# Create Kafka topics
bin/kafka-topics.sh --create --topic raw_reddit_posts --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic processed_reddit_posts --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Running the Pipeline

1. Start the Consumer Script

```console
python3 kafka-reddit-consumer.py
```

2. Run the Archiver Script

```console
python3 archive_reddit.py
```

3. Run the Graph Script

```console
python3 graph_reddit_sent_analysis.py
```

4. Run the WordCloud Script

```console
python3 kafka_wordcloud.py
```

5. Start the Producer Script

```console
python3 kafka-reddit-producer.py
```

6. Retrain the Model (Optional)

```console
python3 sent_analysis.py
```