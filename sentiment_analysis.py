from transformers import pipeline

sentiment_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
data = ["I love you", "I hate you", "I don't know"]
print(sentiment_pipeline(data))

