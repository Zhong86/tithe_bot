import discord
from dotenv import load_dotenv
from agent import agent_executor, run_agent
from datetime import datetime
import asyncio
from functools import partial
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ← add this to .env

async def scheduler():
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.now()
        channel = client.get_channel(CHANNEL_ID)

        # Example: every day at 7pm,
        if now.hour == 19 and now.minute == 0:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(run_agent, "Check this month's tithes and remind the user if anything is due.")
            )
            await channel.send(response)

        # Check every minute
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    client.loop.create_task(scheduler())  # ← start scheduler when bot is ready

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    async with message.channel.typing():
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(run_agent, message.content)
            )
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send(f"⚠️ Something went wrong: {str(e)}")

client.run(os.getenv("BOT_TOKEN"))