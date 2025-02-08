import topic_analysis
import sentiment_analysis
import database
from collections import defaultdict

def get_topic_and_sentiment_analysis(databasE: database.Database):
    """Get the topic and sentiment analysis of the messages"""
    
    topic_analysis_of_messages = topic_analysis.get_topic_analysis(databasE)
    #format of topic_analysis_of_messages: {'TOPICS': [{'TOPIC_NAME': 'topic1', 'TOPIC_RELEVANCE': 100}, {'TOPIC_NAME': 'topic2', 'TOPIC_RELEVANCE': 50}]}
    topics = [x['TOPIC_NAME'] for x in topic_analysis_of_messages['TOPICS']]
    print(topics)

    messages = databasE.get_messages() #json object
    print(messages)

    #create dictionary to store topics and their relevant messages
    topics_and_relevant_messages = defaultdict(list)
    
    #attach messages relevant to topics
    for message in messages:
        content = message[1]
        print(content)
        for topic in topics:
            if topic_analysis.is_sentence_relevant_to_topic(content, topic):
                print(message, "is relevant to ", topic)
                topics_and_relevant_messages[topic].append(content)
    print(topics_and_relevant_messages.values())
    
    topics_and_sentiment_analysis = {}
    topics_and_sentiments = []
    for (topic, messages_relevant_to_topic) in topics_and_relevant_messages.items():
        sentiment_analysis_of_messages = sentiment_analysis.get_sentiment(messages_relevant_to_topic)
        
        topics_and_sentiment_analysis[topic] = sentiment_analysis_of_messages

        positive,negative,neutral = 0,0,0

        for sentiment in sentiment_analysis_of_messages:
            if sentiment['label'] == 'POS':
                positive += 1
            elif sentiment['label'] == 'NEG':
                negative += 1
            else:
                neutral += 1
    
        topics_and_sentiments.append((topic,(positive,negative,neutral)))

    return topics_and_sentiments

def most_active_users_relating_to_topic(databasE: database.Database, topic: str):
    """Get the most active users in relation to a topic"""
    messages = databasE.get_messages()
    print(messages)

    users_and_messages = defaultdict(list)

    for message in messages:
        content = message[1]
        if topic_analysis.is_sentence_relevant_to_topic(content, topic):
            users_and_messages[message[3]].append(content)
    print(users_and_messages)
    return users_and_messages.items()

def get_topics_and_key_contributors(databasE: database.Database):
    """Get the topics and key contributors"""
    topics_and_sentiments = get_topic_and_sentiment_analysis(databasE)
    topics_and_key_contributors = {}
    for topic in topics_and_sentiments:
        key_contributors = most_active_users_relating_to_topic(databasE, topic[0])
        topics_and_key_contributors[topic[0]] = key_contributors
    return topics_and_key_contributors