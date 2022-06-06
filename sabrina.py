import os

import discord

from constants import barrens_chat, trade_chat


client = discord.Client()

MONITORED_CHANNELS = []
MONITORED_CHANNELS += barrens_chat.TEXT_ALL
MONITORED_CHANNELS += trade_chat.TEXT_ALL


@client.event
async def on_ready():
    print(f"{client.user} is online!")



@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return

    if message.channel.id not in MONITORED_CHANNELS:
        return

    if message.author.bot:
        return

    if message.channel.id in MONITORED_CHANNELS:
        if not message.author.bot:
            await message.channel.send(f"Good {message.author.mention}, hide "
                                       "the evidence...", delete_after=3)


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
    if 'hidden like mankrik\'s wife' in msg:
        content = "They must never know our secrets!"

    return content



if __name__ == '__main__':
    TOKEN = os.getenv('TOKEN')
    client.run(TOKEN)
