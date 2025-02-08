import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Set your API key
API_KEY = os.getenv("GEMINI_KEY")
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-pro")

# Function to generate a response
def chat_with_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text  # Extract the text output

topic_classification_prompt = "Here we see a series of messages formatted in a JSON object in the following form {\"MESSAGES\": [{\"USER\": the user who sent the message, \"TIME\": the time at which the message is sent, formatted in natural language typically relative to the current datetime which is _INSERT CURRENT DATETIME, \"MESSAGE\": the content of the message}, ... for all of the messages]}. I want to extract the topics of discussion of the conversation, returned in the form of a JSON object of the form {\"TOPICS\": [{\"TOPIC_NAME\": name of the topic concisely - maximum 3 words, \"TOPIC_RELEVANCE\": a score between 1 to 100 where 100 means this topic is referenced across 100% of messages, and 1 means the topic is referenced across 1% of messages - in general a score of x means a topic is referenced across x% of messages}]}. Here is the object of the messages from the chat INSERT MESSAGES OBJECT
response = chat_with_gemini(user_prompt)
print("Gemini:", response)