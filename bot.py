import logging,os, json, discord
from datetime import datetime, timedelta, timezone
from discord.ext import commands
from discord.message import Message
from dotenv import load_dotenv
from collections import defaultdict
import database
import analysis, topic_analysis
import numpy as np
#-------------------------
load_dotenv()

handler = logging.StreamHandler()

logging.basicConfig(
    handlers=[handler],
)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

database = database.Database()

#-------------------------

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    for guild in client.guilds:
        print(f"Connected to: {guild.name} ({guild.id})")
        for channel in guild.text_channels:
            print(f"Scanning channel: {channel.name}")

            time_limit = datetime.now(timezone.utc) - timedelta(days=7)

            try:
                async for message in channel.history(after=time_limit):
                    if not message.author.bot: log_message(message)
            except discord.Forbidden:
                print(f"No permission to read history in {channel.name}")
    

@client.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bot messages
    log_message(message)
    
    await client.process_commands(message)

def log_message(message: Message):
    database.save_message(message)
    log_entry = f"[{message.guild.name} | #{message.channel.name}] {message.author}: {message.content}"
    logging.info(log_entry)
    print(log_entry)

token = os.getenv("DISCORD_TOKEN")

if token is None:
    raise ValueError("DISCORD_TOKEN is not set")

#-------------------------------------------------------------------------

@client.command()
async def topics_and_opinions(ctx):
    """Get the popular topics and opinions in the server."""
    await ctx.send("Performing analysis...")
    await ctx.send(format_analysis_nicely(analysis.get_topic_and_sentiment_analysis(database)))

@client.command()
async def count_replies(ctx, user: discord.User):
    """Count the number of replies to all messages from the given user."""
    reply_count = 0  # To store the total number of replies
    # Iterate over all channels in the server
    for channel in ctx.guild.text_channels:
        try:
            print(f'📂 Checking channel: {channel.name}')
        
            # Loop through messages in the channel
            async for message in channel.history(limit=500):  # Adjust the limit as needed
                if message.author == user:  # Check if the message is from the target user
                    # Count replies to this message
                    replies = await count_message_replies(channel, message)
                    reply_count += replies
                    print(f'Message by {message.author}: "{message.content}" has {replies} replies')

        except Exception as e:
            print(f'❌ Cannot access channel {channel.name}: {e}')

    await ctx.send(f'Total replies to messages by {user.name}: {reply_count}')

@client.command()
async def count_message_replies(channel, message):
    """Count how many messages are replies to the given message."""
    reply_count = 0
    async for msg in channel.history(limit=100):  # Check the last 100 messages in the channel
        if msg.reference and msg.reference.message_id == message.id:  # If it's a reply to the target message
            reply_count += 1
    return reply_count

@client.command()
async def get_contributors_to_topic(ctx, topic: str):
    await ctx.send(f"Searching messages for contributors to the **{topic}**")

    contributors_and_message_count = defaultdict(int)

    messages = database.get_messages()
    for message in messages:
        if topic_analysis.is_sentence_relevant_to_topic(message[1], topic):
            contributors_and_message_count[message[3]]+=1
    
    sorted_contributors = sorted(contributors_and_message_count.items(), key=lambda x: x[1], reverse=True)
    top_contributors = sorted_contributors[:5]
    output = "Key Contributors to the topic **"+topic+"**:\n"
    if top_contributors == []:
        output += "No contributors detected."
    for user_id, count in top_contributors:
        user = await client.fetch_user(user_id)
        output += f"-{user.mention} ({count} messages)\n"
    await ctx.send(output)

#-------------------------------------------------------------------

def format_analysis_nicely(analysis):
    output = "**📢 Popular Topics:**\n"
    for i in analysis:
        output += f"🔹 {i[0]}\n"

    output += "\n**💬 Opinions:**\n"
    for i in analysis:
        topic, sentiment = i[0], i[1]
        output += (
            f"🔹 **{topic}**\n"
            f"    👍 Positive: {sentiment[0]}\n"
            f"    👎 Negative: {sentiment[1]}\n"
            f"    😐 Neutral: {sentiment[2]}\n"
        )
    return output

@client.command()
async def get_important_users(ctx):

    await ctx.send("Performing analysis...")
    users_and_reactors = defaultdict(list)
    users = ctx.guild.members
    for user in users:
        # Fetch all channels the bot has access to
        if user.name=='CommunityInsights':
            continue
        users_and_reactors[user.name]=[]
        for guild in client.guilds:
            for channel in guild.text_channels:
                try:
                    # Fetch messages in the channel
                    async for message in channel.history(limit=None):
                        if message.author.id == user.id:
                            # Iterate through reactions on the message
                            for reaction in message.reactions:
                                # Fetch users who reacted with this emoji
                                async for user in reaction.users():
                                    if user != client.user:  # Exclude the bot itself
                                        print(message.author, "reacted to", user.name)
                                        users_and_reactors[message.author.name].append(user.name)
                except discord.Forbidden:
                    pass
    print(users_and_reactors)
    result = pagerank(users_and_reactors)
    users_and_importance = []
    for user in result:
        users_and_importance.append((user,result[user]))
    users_and_importance = sorted(users_and_importance, key=lambda x: x[1], reverse =True)
    
    values = [x[1] for x in users_and_importance]
    min_val, max_val = min(values), max(values)
    
    # Avoid division by zero if all values are the same
    if min_val == max_val:
        users_and_importance = [(k, 1.0) for k, v in users_and_importance]  # If all values are the same, set them to 1.0
    else:
       users_and_importance = [(k, (v - min_val) / (max_val - min_val)) for k, v in users_and_importance]

    users_and_importance = users_and_importance[:5]
    output = "Top 5 Users ranked by relative importance:"
    for (a,b) in users_and_importance:
        output+=f"\t-{a},{b}\n"
    await ctx.send(output)

def pagerank(graph, damping_factor=0.85, max_iterations=100, tol=1.0e-6):
    """
    Compute the PageRank of nodes in a directed graph.

    :param graph: A dictionary where keys are nodes and values are lists of nodes they point to.
    :param damping_factor: The probability of following a link (default is 0.85).
    :param max_iterations: Maximum number of iterations (default is 100).
    :param tol: Convergence tolerance (default is 1.0e-6).
    :return: A dictionary of nodes with their corresponding PageRank values.
    """
    # Get all unique nodes in the graph
    nodes = list(graph.keys())
    num_nodes = len(nodes)

    # Initialize the PageRank vector with equal probability
    pagerank_vector = {node: 1 / num_nodes for node in nodes}

    # Create a transition matrix
    transition_matrix = np.zeros((num_nodes, num_nodes))

    # Build the transition matrix
    for i, node in enumerate(nodes):
        if len(graph[node]) == 0:
            # Handle dangling nodes (nodes with no outgoing edges)
            transition_matrix[i, :] = 1 / num_nodes
        else:
            for neighbor in graph[node]:
                j = nodes.index(neighbor)
                transition_matrix[j, i] = 1 / len(graph[node])

    # Add damping factor
    transition_matrix = damping_factor * transition_matrix + (1 - damping_factor) / num_nodes

    # Power iteration to compute PageRank
    for _ in range(max_iterations):
        prev_pagerank_vector = pagerank_vector.copy()
        for i, node in enumerate(nodes):
            pagerank_vector[node] = np.sum(transition_matrix[i, :] * list(prev_pagerank_vector.values()))

        # Check for convergence
        diff = sum(abs(pagerank_vector[node] - prev_pagerank_vector[node]) for node in nodes)
        if diff < tol:
            break

    return pagerank_vector

client.run(token, log_handler=handler) #start the bot
