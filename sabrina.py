import logging
import os
import random

import discord

from Assistant import DiscordBot
from bot_utils.sabrina import Parser
from constants import users
from constants.guilds import barrens_chat, trade_chat


class Sabrina(DiscordBot):
    def __init__(self, user_id=users.SABRINA, name="Sabrina", channels=None):
        super(Sabrina, self).__init__(user_id, name, channels)
        self.negative_responses = [
            "You *dare* challenge **ME**?",
            "I don't see *you* doing much better!"
        ]

    def _is_talking_to_me(self, msg, raw_mentions):
        return self._is_mentioned(self.name, msg, self.id, raw_mentions)

    def _is_seth_mentioned(self, msg, raw_mentions):
        name = 'seth'
        return self._is_mentioned(name, msg, users.SETH, raw_mentions)

    def _num_members(self, channel_members, members_to_check):
        count = 0
        for member in members_to_check:
            if member in channel_members:
                count += 1
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

    # async def on_member_update(self, member, before, after):
    #     print(member)
    #     print(before)
    #     print(after)

    async def on_voice_state_update(self, member, before, after):
        if (channel := after.channel) is not None:
            general = self.channels[barrens_chat.TEXT_GENERAL]
            if channel.id == barrens_chat.VOICE_CHILL_LOUNGE:
                if member.id == users.SOUMALY:
                    await self.fake_type(general, 2)
                    content = f"Here comes {member.mention} to steal MVP!"
                    await general.send(content, delete_after=10)

            num = self._num_members(channel.members, users.ALL_REAL_USERS)
            if num > 4:
                await self.fake_type(general, 2)
                content = "Holy shit, the gang's all here!"
                await general.send(content, delete_after=10)
            elif num > 3:
                await self.fake_type(general, 2)
                content = f"Hey look, even {member.mention} is on."
                await general.send(content, delete_after=10)

    async def on_message_delete(self, message):
        message, deleter, respond = await super().on_message_delete(message)
        if respond:
            channel = message.channel
            await self.fake_type(channel)
            resp = f"Good {deleter.mention}, hide the evidence..."
            await channel.send(resp, delete_after=10)

    async def respond_to_bot(self, message):
        msg = message.content.casefold()

        if 'do a better job' in msg:  # CrossRoads Bot
            await self.fake_type(message.channel)
            content = random.choice(self.negative_responses)
            await message.reply(content, delete_after=5)
        elif 'going to play Heroes' in msg:  # CrossRoads Bot
            await self.fake_type(message.channel)
            if users.SOUMALY in message.channel.members:
                soumaly = await self.fetch_user(users.SOUMALY)
                content = f"I wonder who MVP will be..." \
                          f"*cough*{soumaly.mention}*cough*"
            else:
                content = "Looks like a possible game night to me!"
            await message.reply(content, delete_after=5)

    async def respond_to_human(self, message):
        msg = message.content.casefold()

        talking_to_me = self._is_talking_to_me(msg, message.raw_mentions)
        talking_to_seth = self._is_seth_mentioned(msg, message.raw_mentions)

        if talking_to_me or talking_to_seth:
            parser = Parser(message.content)
            handlers = parser.parse().find_handler()
            for handler in handlers:
                await handler(message)


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

    sabrina = Sabrina(
        channels=authorized_channels
    )
    sabrina.run(TOKEN)


if __name__ == '__main__':
    main()
