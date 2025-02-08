import google.generativeai as genai
from dotenv import load_dotenv
import os
import database
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

load_dotenv()

# Set your API key
API_KEY = os.getenv("GEMINI_KEY")
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-pro")

# Function to generate a response
def get_topic_analysis(databasE: database.Database) -> json:
    processed_messages = messages_preprocessing(databasE)
    prompt = f"""Here we see a series of messages formatted in a JSON object in the following form
{{"MESSAGES": [{{"USER": the user who sent the message, "TIME": the time at which the message is sent, formatted in natural language typically relative to the current datetime which is _INSERT CURRENT DATETIME, "MESSAGE": the content of the message}}, ... for all of the messages]}}. I want to extract the topics of discussion of the conversation, returned in the form of a JSON object of the form {{"TOPICS": [{{"TOPIC_NAME": name of the topic concisely - maximum 3 words, "TOPIC_RELEVANCE": a score between 1 to 100 where 100 means this topic is referenced across 100% of messages, and 1 means the topic is referenced across 1% of messages - in general a score of x means a topic is referenced across x% of messages}}]}}. Here is the object of the messages from the chat {processed_messages}"""
    response = model.generate_content(prompt)
    return json.loads(response.text)  # Extract the text output

def messages_preprocessing(databasE: database.Database) -> json:
    # messages have format (id, content, timestamp, user_id, channel_id)
    """given messages, process them into a json {MESSAGES: [USER, TIME, MESSAGE]}"""
    messages = databasE.get_messages()
    json_messages_values = [
        {
            "USER": message[3],
            "TIME": message[2],
            "MESSAGE": message[1].lower()
            }
            for message in messages
        ]
    for i in json_messages_values:
        print(i)
    json_output = {"MESSAGES": json_messages_values}
    return json_output

#response = chat_with_gemini(user_prompt)
#print("Gemini:", response))


def is_sentence_relevant_to_topic(sentence: str, topic: str) -> bool:
    threshold = 0.2
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([sentence, topic])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return similarity >= threshold

print(is_sentence_relevant_to_topic("I love you", "love"))