import discord
from dotenv import load_dotenv
from agent import agent_executor
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    response = agent_executor.invoke({"messages": [("human", message.content)]})
    await message.channel.send(response["messages"][-1].content)

client.run(os.getenv("BOT_TOKEN"))