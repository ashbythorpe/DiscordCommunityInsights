import logging,os, json, discord
from datetime import datetime, timedelta, timezone
from discord.ext import commands
from discord.message import Message
from dotenv import load_dotenv

import database
import analysis
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
                    log_message(message)
            except discord.Forbidden:
                print(f"No permission to read history in {channel.name}")


@client.event
async def on_message(message):
    if message.content.startswith("!"):
        if message.content=="!topicsAndOpinions":
            await message.channel.send("Performing analysis...")
            await message.channel.send(format_analysis_nicely(analysis.get_topic_and_sentiment_analysis(database)))
            return
        if message.content=="!topicsAndUsers":
            await message.channel.send("Performing analysis...")
            await message.channel.send(analysis.get_topics_and_key_contributors(database))
    elif message.author.bot:
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

#print(analysis.get_topic_and_sentiment_analysis(database))

def format_analysis_nicely(analysis):
    output = ""
    output = output+("**Popular topics:**\n")
    for i in analysis:
        output = output+(f"-{i[0]}\n")

    output = output+("\n**Opinions:**\n")
    for i in analysis:
        output = output+(f"-{i[0]}: {i[1][0]} positive, {i[1][1]} negative, {i[1][2]} neutral comments \n")    
    return output

client.run(token, log_handler=handler) #start the bot
