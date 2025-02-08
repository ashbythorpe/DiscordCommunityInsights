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
    prompt = f"""You are an AI assistant that extracts key discussion topics from conversations.  
        Analyze the following messages and return a JSON object in this format:  
        {{
        "TOPICS": [
            {{"TOPIC_NAME": "Topic 1", "TOPIC_RELEVANCE": 85}},
            {{"TOPIC_NAME": "Topic 2", "TOPIC_RELEVANCE": 65}},
            {{"TOPIC_NAME": "Topic 3", "TOPIC_RELEVANCE": 30}}
        ]
        }}
    The input is a **JSON object** with chat messages in this format:
        {{
            "MESSAGES": [
                {{
                    "USER": "421359636524957706",
                    "TIME": "2025-02-08 14:09:37.185000+00:00",
                    "MESSAGE": "What do you guys think about AI ethics?"
                }},
                {{
                    "USER": "267219922558517259",
                    "TIME": "2025-02-08 14:09:43.643000+00:00",
                    "MESSAGE": "AI regulation is really important nowadays."
                }},
                {{
                    "USER": "537311422305140746",
                    "TIME": "2025-02-08 14:10:01.231000+00:00",
                "MESSAGE": "I agree, especially with bias in AI models."
                }},
                {{
                    "USER": "421359636524957706",
                    "TIME": "2025-02-08 14:13:01.443000+00:00",
                    "MESSAGE": "Yeah, bias in AI is a huge issue."
                }}
                ]
        }}
        Now, process this input and extract key topics: {processed_messages}"""
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