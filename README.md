# DiscordCommunityInsights

Discord bot built on Python.

Uses: discord.py

Messages scraped are stored in a SQLite database. 

User interacts with bot through commands on discord

Commands:
 - topics_and_opinions()
    Scrapes through all messages sent in the servers it is a part of in the last seven days.
    Through prompting Gemini and inputting the messages, we produce a list of key topics discussed.
    Then, we iterate through all the messages and attach the relevant key topics to the message by using a vector similarity approach
    The sentiments of the topic are then analysed by performing sentiment analysis on each of the messages associated with each topic
    The sentiment analysis uses the "finiteautomata/bertweet-base-sentiment-analysis" model
    The sentiment analysis returns the number of comments that have positive sentiment, negative sentiment, and neutral sentiment for each topic
    This information is then outputted to the discord channel the command was invoked in. 
 - get_important_users()
    The bot finds users that have reacted to other user's messages.
    It forms a directed graph with this information.
    It then ranks each user using the PageRank algorithm
 - get_contributors_to_topic(topic)
    Given a topic, iterate through all messages, determine whether the sentence talks about the topic using a vector similarity approach.
    Then if deemed similar, the user is added as a contributor to the topic
    List of contributors is returned.