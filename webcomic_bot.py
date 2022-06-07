# https://discordpy.readthedocs.io/en/stable/ext/commands/api.html
# Permissions: 292058168384

import logging
import os

import discord
from discord.ext import commands as disc_commands

from bot_utils.webcomic import Darklegacy
from constants.guilds import barrens_chat


AUTHORIZED_CHANNELS = [
    barrens_chat.TEXT_WEBCOMIC
]

SUPPORTED_COMICS = {
    # Title: Tuple of keywords
    'Dark Legacy': ('dark', 'legacy')
}


bot = disc_commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    """
    Sets the channels property.
    This method is called when the Bot is ready to serve
    client responses on Discord.
    :return: None
    """

    watching = discord.ActivityType.watching
    name = "webcomics channel"
    activity = discord.Activity(type=watching, name=name)
    await bot.change_presence(activity=activity)
    logging.debug(f"{bot.user} is online!")


def ignored(message):
    """
    Filters out messages that should be ignored to prevent
    looping of bots talking to themselves or each other.
    :param message: Discord Message object
    :return: Boolean of whether or not the message should be
    ignored
    """

    ignore = False
    if message.author == bot.user:
        ignore = True
    elif message.channel.id not in AUTHORIZED_CHANNELS:
        ignore = True
    return ignore


def find_comic(args):
    """
    Searches through supported comics for the requested comic name.
    :param args: Tuple of keyword arguments passed to the bot
    :return: String name of supported comic if found
    """

    for title, keywords in SUPPORTED_COMICS.items():
        if all(word in (arg.casefold() for arg in args) for word in keywords):
            comic_name = title
            break
    else:
        comic_name = None
    return comic_name


async def webcomic_download(message, comic_name, _tmp):
    channel = await bot.fetch_channel(barrens_chat.TEXT_WEBCOMIC)
    await channel.trigger_typing()

    try:
        if comic_name == 'Dark Legacy':
            dark_legacy = Darklegacy()
            comics = [dark_legacy.get_latest_comic()]
            for comic in comics:
                content = f"{message.author.mention} your {comic_name}" \
                          "comic has arrived!"
                embed = dark_legacy.embed(comic)
                await channel.send(content=content, embed=embed)
    except Exception as e:
        print(e)
        await message.reply("I couldn't do it for the following "
                            "reasons:\n" + str(e))
    finally:
        await _tmp.delete()
        await message.delete()


@bot.command('download')
async def download_comic(ctx, *args, **kwargs):
    message = ctx.message

    if ignored(message):
        return

    if (comic_name := find_comic(args)) is not None:
        # first = any('latest' == arg.casefold() for arg in args)
        # latest = any('latest' == arg.casefold() for arg in args)
        content = f"Searching for the latest {comic_name} comic..."
        _tmp = await message.reply(content)
        await webcomic_download(message, comic_name, _tmp)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] %(message)s'
    )
    logging.getLogger('discord').setLevel(logging.WARNING)

    if (TOKEN := os.environ.get('TOKEN')) is None:
        raise ValueError("Please set the TOKEN environment variable.")

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
