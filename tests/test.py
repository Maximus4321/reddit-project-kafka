import joblib

model = joblib.load('../config/sentiment_model.pkl')
vectorizer = joblib.load('../config/vectorizer.pkl')

tests = [
    {"text": "I really loved this movie, it was amazing!", "expected": "positive"},
    {"text": "This is the worst product I have ever bought.", "expected": "negative"},
    {"text": "The service was okay, not too good, not too bad.", "expected": "negative"},
    {"text": "Absolutely fantastic! I'm so happy with it.", "expected": "positive"},
    {"text": "I'm very disappointed with the quality of this item.", "expected": "negative"},
]

texts = [case["text"] for case in tests]
expected = [case["expected"] for case in tests]
vectors = vectorizer.transform(texts)
pred = model.predict(vectors)
for text, predicted, expected in zip(texts, pred, expected):
    success = "Success" if predicted == expected else "Fail"
    print(f"Text: {text}")
    print(f"Predicted Sentiment: {predicted}")
    print(f"Expected Sentiment: {expected}")
    print(f"Test Result: {success}\n")
