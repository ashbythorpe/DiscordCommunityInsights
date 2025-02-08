import sqlite3
from transformers import pipeline

DATABASE_FILE = "database.db"

def read_messages():
    """Connect to the database and read all messages"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Messages")
        messages = cursor.fetchall()

        print("Messages:")
        for msg in messages:
            print(msg)

        conn.close()
    except sqlite3.Error as e:
        print(e)

sentiment_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
data = ["I love you", "I hate you", "I don't know"]
print(sentiment_pipeline(data))


