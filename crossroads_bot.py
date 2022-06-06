import logging
import os
import time

from Assistant import DiscordBot
from constants import users
from constants.guilds import barrens_chat


class CrossRoadsBot(DiscordBot):
    def __init__(self, user_id=users.CROSSROADS_BOT, name="CrossRoads Bot",
                 channels=None):
        super(CrossRoadsBot, self).__init__(user_id, name, channels)

    async def on_message_delete(self, message):
        message, deleter, respond = await super().on_message_delete(message)
        if respond:
            resp = "Hidden like Mankrik's wife..."
            await message.channel.send(resp, delete_after=7)

    async def respond_to_bot(self, message):
        content = None

        msg = message.content.casefold()

        if 'the evidence...' in msg:
            content = "Let's hope you do a better job than last time..."

        if content is not None:
            await message.channel.trigger_typing()
            time.sleep(2)
            await message.reply(content, delete_after=5)

    async def respond_to_human(self, message):
        # Extended times on bot messages by 2 seconds and ran tests.
        msg = message.content.casefold()  # Case insensitive

        if '!help' in msg:
            await message.reply("I can't help you with that", delete_after=5)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] %(message)s'
    )
    logging.getLogger('discord').setLevel(logging.WARNING)

    if (TOKEN := os.environ.get('TOKEN')) is None:
        raise ValueError("Please set the TOKEN environment variable.")

    authorized_channels = barrens_chat.TEXT_ALL
    authorized_channels.remoace(barrens_chat.TEXT_WEBCOMIC)

    crossroads_bot = CrossRoadsBot(
        channels=authorized_channels
    )
    crossroads_bot.run(TOKEN)


if __name__ == '__main__':
    main()
