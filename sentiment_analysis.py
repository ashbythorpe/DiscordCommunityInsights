import sqlite3
import database

def get_sentiment(messages: list[str]) -> list[str]:
    from transformers import pipeline
    """Given a list of strings, return an object [{label: '', score: ''}]"""
    sentiment_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
    return sentiment_pipeline(messages)

#print(get_sentiment(["I love you", "I hate you", "I don't know"]))

#database.read_messages()
