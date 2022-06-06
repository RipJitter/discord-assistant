import os

import discord

from constants import barrens_chat


client = discord.Client()

MONITORED_CHANNELS = [
    barrens_chat.TEXT_GENERAL,
]


@client.event
async def on_ready():
    print(f"{client.user} is online!")


@client.event
async def on_message_delete(message):
    if message.author == client.user or message.author.bot:
        return

    if message.channel.id not in MONITORED_CHANNELS:
        return

    await message.channel.send(f"Hidden like Mankrik's wife...",
                               delete_after=7)


@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    if message.channel.id not in MONITORED_CHANNELS:
        return
#Extened times on bot messages by 2 seconds and ran tests.
    msg = message.content.casefold()  # Case insensitive
    if '!help' in msg:
        await message.reply("I can't help you with that", delete_after=5)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id not in MONITORED_CHANNELS:
        return

    msg = message.content.casefold()

    if message.author.bot:
        content = respond_to_bot(msg)
        if content is not None:
            await message.reply(content, delete_after=2)


def respond_to_bot(msg):
    content = None
    if 'the evidence...' in msg:
        content = "Grabbing the shovel!"

    return content

if __name__ == '__main__':
    TOKEN = os.getenv('TOKEN')
    client.run(TOKEN)
