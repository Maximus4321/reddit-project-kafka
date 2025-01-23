import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os

def load_datasets(main_file, feedback_file):
    main_df = pd.read_csv(main_file, encoding='latin-1', names=["polarity", "id", "date", "query", "user", "text"])
    main_df["sentiment"] = main_df["polarity"].apply(lambda x: "positive" if x == 4 else "negative")
    main_df = main_df[["text", "sentiment"]]
    feedback_df = None
    if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
        feedback_df = pd.read_csv(feedback_file)
    if feedback_df is not None:
        combined_df = pd.concat([main_df, feedback_df], ignore_index=True)
    else:
        combined_df = main_df
    return combined_df

def preprocess_data(df):
    tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    X = tfidf_vectorizer.fit_transform(df["text"])
    y = df["sentiment"]
    return X, y, tfidf_vectorizer

def train_model(X, y):
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model

def save_model(model, vectorizer, model_filename="config/sentiment_model.pkl", vectorizer_filename="config/vectorizer.pkl"):
    joblib.dump(model, model_filename)
    joblib.dump(vectorizer, vectorizer_filename)

def main():
    combined_df = load_datasets('config/sentiment140.csv', 'config/userfeedback.csv')
    X, y, vectorizer = preprocess_data(combined_df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = train_model(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy * 100:.2f}%")
    save_model(model, vectorizer)
    print("Model retrained and saved!")

if __name__ == "__main__":
    main()
