import os
import re

import discord

from constants import barrens_chat, trade_chat, users


client = discord.Client()

MONITORED_CHANNELS = []
MONITORED_CHANNELS += barrens_chat.TEXT_ALL
MONITORED_CHANNELS += trade_chat.TEXT_ALL
MONITORED_CHANNELS.remove(barrens_chat.TEXT_WEBCOMIC)


@client.event
async def on_ready():
    print(f"{client.user} is online! delete a message in discord! ")


@client.event
async def on_voice_state_update(member, before, after):
    if after.channel.id == barrens_chat.VOICE_CHILL_LOUNGE:
        general = client.get_channel(barrens_chat.TEXT_GENERAL)
        if member.id == users.SOUMALY:
            await general.send(f"Here comes {member.mention} to steal MVP!")

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
            # if message.channel.id != barrens_chat.TEXT_GENERAL:
                resp = f"Good {message.author.mention}, hide the evidence..."
                await message.channel.send(resp, delete_after=3)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id not in MONITORED_CHANNELS:
        return

    if message.author.bot:
        content = respond_to_bot(message)
        if content is not None:
            await message.reply(content, delete_after=2)
    else:
        content = respond_to_human(message)
        if content is not None:
            await message.reply(content)


def respond_to_human(message):
    content = None

    msg = message.content.casefold()

    if 'sabrina' in msg or users.SABRINA in message.raw_mentions:
        pattern = re.compile(
            r'hi|hello|greetings|hiya|hey|hola'
        )
        if re.search(pattern, msg):
            content = hello(message)

    if 'seth' in msg or users.SETH in message.raw_mentions:
        pattern = re.compile(
            r'how\s+do\s+(?:i|you)'
        )
        if re.search(pattern, msg):
            content = lmgt(msg)

    return content

def hello(message):
    content = f"Hello {message.author.mention}."
    return content


def lmgt(msg):
    lmgt = 'https://letmegooglethat.com'

    if '?' in msg:
        msg = msg.split('?')[0]

    if 'seth' in msg:
        msg = re.sub(r'seth', '', msg)

    query = re.sub(r'[^\w]+', '+', msg)
    if query.endswith('+'):
        query = query[:-1]
    content = f"{lmgt}/?q={query}"

    return content


def respond_to_bot(msg):
    content = None
    if 'hidden like mankrik\'s wife' in msg:
        content = "They must never know our secrets!"
    return content


if __name__ == '__main__':
    TOKEN = os.getenv('TOKEN')
    client.run(TOKEN)
