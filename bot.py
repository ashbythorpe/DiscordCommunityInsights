import logging
import os
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from discord.guild import Guild
from discord.message import Message
from dotenv import load_dotenv

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
    if message.author.bot:
        return  # Ignore bot messages
    log_message(message)
    await client.process_commands(message)


def log_message(message: Message):
    log_entry = f"[{message.guild.name} | #{message.channel.name}] {message.author}: {message.content}"
    logging.info(log_entry)
    print(log_entry)


token = os.getenv("DISCORD_TOKEN")

if token is None:
    raise ValueError("DISCORD_TOKEN is not set")

client.run(token, log_handler=handler)
