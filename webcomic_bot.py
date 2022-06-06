# Permissions: 292058168384
import logging
import os

from Assistant import DiscordBot
from bot_utils.webcomic import Darklegacy
from constants import users
from constants.guilds import barrens_chat


class WebComicBot(DiscordBot):
    SUPPORTED_COMICS = [
        'Dark Legacy'
    ]

    def __init__(self, user_id=users.WEBCOMIC_BOT, name="WebComic Bot",
                 channels=None):
        super(WebComicBot, self).__init__(user_id, name, channels)

    def _supported_comic_mentioned(self, msg):
        return any(comic.casefold() in msg for comic in self.SUPPORTED_COMICS)

    def _find_mentioned_comic(self, msg):
        for comic in self.SUPPORTED_COMICS:
            if comic.casefold() in msg:
                mentioned_comic = comic
                break
        else:
            mentioned_comic = None
        return mentioned_comic

    async def respond_to_human(self, message):
        msg = message.content.casefold()

        if 'download' in msg and self._supported_comic_mentioned(msg):
            comic_name = self._find_mentioned_comic(msg)
            content = f"Searching for the latest {comic_name} comic..."
            _tmp = await message.reply(content)
            await self.webcomic_download(message, comic_name, _tmp)

    async def webcomic_download(self, message, comic_name, _tmp):
        channel = self.channels[barrens_chat.TEXT_WEBCOMIC]
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


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] %(message)s'
    )
    logging.getLogger('discord').setLevel(logging.WARNING)

    if (TOKEN := os.environ.get('TOKEN')) is None:
        raise ValueError("Please set the TOKEN environment variable.")

    authorized_channels = [barrens_chat.TEXT_WEBCOMIC]

    web_comic_bot = WebComicBot(channels=authorized_channels)
    web_comic_bot.run(TOKEN)


if __name__ == '__main__':
    main()
