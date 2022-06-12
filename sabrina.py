import logging
import os

import discord

from Assistant import DiscordBot
from bot_utils.sabrina.ai import Searcher
from bot_utils.sabrina import banter
from constants import users
from constants.guilds import barrens_chat, trade_chat


class Sabrina(DiscordBot):
    def __init__(self, user_id=users.SABRINA, name="Sabrina", channels=None,
                 intents=None):
        super(Sabrina, self).__init__(user_id, name, channels, intents)
        self.greeting_responses = [
            "Hello {message.author.mention}.",
            "Hi {message.author.mention}.",
            "What's up?",
            "Hey.",
        ]
        self.complete_responses = [
            "Okay {message.author.mention}.",
            "Done.",
            "Too easy!",
            "Anything else {message.author.mention}?"
        ]
        self.negative_responses = [
            "You *dare* challenge **ME**?",
            "I don't see *you* doing much better, {message.author.mention}!"
        ]

    def _is_talking_to_me(self, msg, raw_mentions):
        return self._is_mentioned(self.name, msg, self.id, raw_mentions)

    def _is_seth_mentioned(self, msg, raw_mentions):
        name = 'seth'
        return self._is_mentioned(name, msg, users.SETH, raw_mentions)

    def _num_members(self, channel_members, members_to_check):
        count = len([m for m in members_to_check if m in channel_members])
        return count

    async def on_ready(self):
        """
        Sets the channels property.
        This method is called when the Bot is ready to serve
        client responses on Discord.
        :return: None
        """

        await super().on_ready()
        watching = discord.ActivityType.watching
        name = "everything"
        activity = discord.Activity(type=watching, name=name)
        await self.change_presence(activity=activity)

    async def on_voice_state_update(self, member, before, after):
        if (channel := after.channel) is not None:  # someone joined
            await banter.joined_voice_chat(self, member, before, after)

            if channel.id == barrens_chat.VOICE_CHILL_LOUNGE:
                await banter.joined_chill_lounge(self, member, before, after)

    async def on_message_delete(self, message):
        message, deleter, respond = await super().on_message_delete(message)
        if respond:
            await banter.message_deleted(self, message, deleter)

    async def respond_to_bot(self, message):
        await banter.bot_routine(self, message)

    async def respond_to_human(self, message):
        msg = message.content.casefold()

        talking_to_me = self._is_talking_to_me(msg, message.raw_mentions)
        talking_to_seth = self._is_seth_mentioned(msg, message.raw_mentions)

        if talking_to_me or talking_to_seth:
            logging.debug(f"{message.author.name} is talking to me")
            handlers = Searcher(message.content).find_handlers()
            for handler in handlers:
                await handler(self, message)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] %(message)s'
    )
    logging.getLogger('discord').setLevel(logging.WARNING)

    if (TOKEN := os.environ.get('TOKEN')) is None:
        raise ValueError("Please set the TOKEN environment variable.")

    authorized_channels = barrens_chat.TEXT_ALL
    authorized_channels += trade_chat.TEXT_ALL
    authorized_channels.remove(barrens_chat.TEXT_WEBCOMIC)

    intents = discord.Intents().all()

    sabrina = Sabrina(
        channels=authorized_channels,
        intents=intents
    )
    sabrina.run(TOKEN)


if __name__ == '__main__':
    main()
