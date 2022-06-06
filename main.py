# Permissions: 292058168384

import discord
import os

from webcomic import Darklegacy


client = discord.Client()


TOKEN = os.getenv('TOKEN')

GENERAL_CHANNEL_ID = 684222666709794844
READ_BEFORE_POSTING_CHANNEL_ID = 829856328444674058
NSFW_MEMES18PLUS = 981730567118807050
NMS_CHANNEL_ID = 982888443782787142
WEBCOMIC_CHANNEL_ID = 983109433699741696

MONITORED_CHANNELS = [
    GENERAL_CHANNEL_ID,
    READ_BEFORE_POSTING_CHANNEL_ID,
    NSFW_MEMES18PLUS,
    NMS_CHANNEL_ID,
    WEBCOMIC_CHANNEL_ID
]

SUPPORTED = [
    'Dark Legacy'
]


@client.event
async def on_ready():
    print(f"{client.user} is online!")


@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return

    if message.channel.id in MONITORED_CHANNELS:
        await message.channel.send(f"Good {message.author.mention}, hide the "
                                   "evidence...", delete_after=3)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id == WEBCOMIC_CHANNEL_ID:
        await webcomic_cmd(message)


async def webcomic_cmd(message):
    msg = message.content.casefold()

    if 'download' in msg and any(c.casefold() in msg for c in SUPPORTED):
        _tmp = await message.reply("Yes daddy...")
        await webcomic_download(message, msg, _tmp)


async def webcomic_download(message, msg, _tmp):
    channel = client.get_channel(WEBCOMIC_CHANNEL_ID)
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
    client.run(TOKEN)
