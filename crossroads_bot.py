import discord

from constants import *


client = discord.Client()

MONITORED_CHANNELS = [
    GENERAL_CHANNEL_ID,
]


@client.event
async def on_ready():
    print(f"{client.user} is online!")


@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return

    if message.channel.id in MONITORED_CHANNELS:
        if not message.author.bot:
            await message.channel.send(f"Hidden like Mankrik's wife...",
                                       delete_after=3)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.author.bot:
        msg = message.content.casefold()  # Case insensitive
        if '!help' in msg:
            await message.reply("I can't help you with that", delete_after=5)


if __name__ == '__main__':
    client.run(TOKEN)
