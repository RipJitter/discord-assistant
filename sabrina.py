import discord

from constants import *


client = discord.Client()

MONITORED_CHANNELS = [
    GENERAL_CHANNEL_ID,
    READ_BEFORE_POSTING_CHANNEL_ID,
    NSFW_MEMES18PLUS,
    NMS_CHANNEL_ID,
    WEBCOMIC_CHANNEL_ID
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
            await message.channel.send(f"Good {message.author.mention}, hide "
                                       "the evidence...", delete_after=3)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.bot:
        if 'hide the evidence' in message.content.casefold():
            await message.reply("They must never know our secrets!",
                                delete_after=2)


if __name__ == '__main__':
    client.run(TOKEN)
