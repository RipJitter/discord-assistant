"""
This file serves as an example of a Discord bot implementation via
a class Object. You should not use this file directly, but subclass
the DiscordBot class within this module.
"""


from datetime import datetime, timedelta
import logging
import os

import discord


class DiscordBot(discord.Client):
    """
    Discord Bot client implementation example. A good use-case
    would be to subclass this class and overwrite the methods you
    want to change. You can call the parent class's (this class's)
    methods like this "x = super().overwritten_class_method(args)"
    """

    def __init__(self, channels=None):
        """
        Initializes the Bot class.
        :param channels: List of channels to authorize the bot to
        operate within.
        """

        super(DiscordBot, self).__init__()
        if channels is None:
            channels = []
        self.authorized_channels = channels
        self.channels = {}  # id: Channel

    def _ignored(self, message):
        """
        Filters out messages that should be ignored to prevent
        looping of bots talking to themselves or each other.
        :param message: Discord Message object
        :return: Boolean of whether or not the message should be
        ignored
        """

        ignored = False
        if message.author == self.user:
            ignored = True
        elif message.channel.id not in self.authorized_channels:
            ignored = True
        return ignored

    @staticmethod
    async def _find_deleter(message):
        """
        Searches through a Discord guild audit log for
        message_delete actions to determine the user that deleted a
        message.
        :param message: Discord Message object
        :return: Discord User object that deleted the message
        """

        action = discord.AuditLogAction.message_delete
        now = datetime.utcnow()
        one_second_ago = now - timedelta(seconds=1)

        async for entry in message.guild.audit_logs(limit=1, action=action):
            if now > entry.created_at > one_second_ago:
                deleter = entry.user
                msg = f"{deleter.name} deleted {message.author.name}'s message"
                logging.debug(msg)
                break
        else:
            deleter = message.author
            logging.debug(f"{deleter} deleted their own message")

        return deleter

    def _get_channels(self):
        """
        Gets a dictionary containing Channel objects from the
        authorized_channels property. This allows for quick access
        to channels by their ID.
        :return: Dictionary of Channels by ID
        """

        channels = {c: self.get_channel(c) for c in self.authorized_channels}
        names = [c.name for c in channels.values()]
        logging.debug(f"Monitoring the following channels: {', '.join(names)}")
        return channels

    async def on_ready(self):
        """
        Sets the channels property.
        This method is called when the Bot is ready to serve
        client responses on Discord.
        :return: None
        """

        self.channels = self._get_channels()
        logging.debug(f"{self.user} is online!")

    async def on_message_delete(self, message):
        """
        Finds the deleter of a message and suggests if the bot
        should respond.
        This method is called when a message that was posted while
        the bot was online was deleted.
        :param message: Discord Message object that was deleted
        :return: Tuple containing the deleted message, the User
        that deleted the message, and a Boolean value suggesting if
        the Bot should respond or not.
        """

        if self._ignored(message):
            return

        msg = "Message deleted. Checking audit log to see if I should respond"
        logging.debug(msg)
        should_respond = False

        deleter = await self._find_deleter(message)

        if not deleter.bot:
            should_respond = True

        return message, deleter, should_respond

    async def on_message(self, message):
        """
        Responds to messages within Discord.
        This method is called when a message was posted to one
        of the channels in the bot's authorized_channels property.
        :param message: Discord Message object that was sent
        :return: None by default, should be overwritten
        """

        if self._ignored(message):
            return

        if message.author.bot:
            response = await self.respond_to_bot(message)
        else:
            response = await self.respond_to_human(message)
        return response

    async def respond_to_bot(self, message):
        """
        You should overwrite this method in your subclass with
        commands to issue when a bot sends a message in a channel
        that this bot has in it's authorized_channels property.
        :param message: Discord Message object
        :return: None by default, should be overwritten
        """

        pass  # Overwrite me!

    async def respond_to_human(self, message):
        """
        You should overwrite this method in your subclass with
        commands to issue when a bot sends a message in a channel
        that this bot has in it's authorized_channels property.
        :param message: Discord Message object
        :return: None by default, should be overwritten
        """

        pass  # Overwrite me!


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] %(message)s'
    )
    logging.getLogger('discord').setLevel(logging.WARNING)

    if (TOKEN := os.environ.get('TOKEN')) is None:
        raise ValueError("Please set the TOKEN environment variable.")

    authorized_channels = []  # Replace me

    bot = DiscordBot(authorized_channels)
    bot.run(TOKEN)
