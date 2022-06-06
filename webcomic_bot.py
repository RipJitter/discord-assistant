# Permissions: 292058168384
import os

import discord

from constants import barrens_chat
from bot_utils.webcomic import Darklegacy


client = discord.Client()

MONITORED_CHANNELS = [
    barrens_chat.TEXT_WEBCOMIC
]

SUPPORTED = [
    'Dark Legacy'
]


@client.event
async def on_ready():
    print(f"{client.user} is online!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id not in MONITORED_CHANNELS:
        return

    if message.author.bot:
        return

    msg = message.content.casefold()

    if 'download' in msg and any(c.casefold() in msg for c in SUPPORTED):
        _tmp = await message.reply("Searching for the latest comic...")
        await webcomic_download(message, msg, _tmp)


async def webcomic_download(message, msg, _tmp):
    channel = client.get_channel(barrens_chat.TEXT_WEBCOMIC)
    try:
        await channel.trigger_typing()
        if 'dark legacy' in msg:
            dark_legacy = Darklegacy()
            comics = [dark_legacy.get_latest_comic()]
            for comic in comics:
                content = f"{message.author.mention} your Dark Legacy comic " \
                          f"has arrived!"
                embed = dark_legacy.embed(comic)
                await channel.send(content=content, embed=embed)
    except Exception as e:
        print(e)
        await message.reply("I couldn't do it for the following "
                            "reasons:\n" + str(e))
    finally:
        await _tmp.delete()
        await message.delete()


if __name__ == '__main__':
    TOKEN = os.getenv('TOKEN')
    client.run(TOKEN)
