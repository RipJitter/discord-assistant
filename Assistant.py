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

    def __init__(self, user_id=0, name="DiscordBot", channels=None):
        """
        Initializes the Bot class.
        :param channels: List of channels to authorize the bot to
        operate within.
        """

        super(DiscordBot, self).__init__()
        self.id = user_id
        self.name = name
        if channels is None:
            channels = []
        self.authorized_channels = channels
        self.channels = {}  # id: Channel

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

    @staticmethod
    def _is_mentioned(name=None, msg=None, user_id=None, raw_mentions=None):
        """
        Checks to see if a Discord user is mentioned in a message.
        :param name: String name of user
        :param msg: String message content to search in
        :param user_id: Discord User ID number of the user
        :param raw_mentions: List of Discord User IDs mentioned
        :return: Boolean of whether the user was mentioned or not
        """

        is_mentioned = False

        _name = name is not None
        _msg = msg is not None
        if all((_name, _msg)):
            if name in msg:
                is_mentioned = True

        _user_id = user_id is not None
        _raw_mentions = raw_mentions is not None
        if all((_user_id, _raw_mentions)):
            if user_id in raw_mentions:
                is_mentioned = True

        return is_mentioned

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

        ignored = False
        if self._ignored(message):
            ignored = True

        msg = "Message deleted. Checking audit log to see if I should respond"
        logging.debug(msg)
        should_respond = False

        if not ignored:
            try:
                deleter = await self._find_deleter(message)
            except discord.errors.Forbidden:
                deleter = None

            if deleter is not None and not deleter.bot:
                should_respond = True
        else:
            deleter = None

        return message, deleter, should_respond

    async def on_message(self, message):
        """
        Responds to messages within Discord.
        This method is called when a message was posted to one
        of the channels in the bot's authorized_channels property.
        :param message: Discord Message object that was sent
        :return: Discord Message object
        """

        if self._ignored(message):
            return

        if message.author.bot:
            await self.respond_to_bot(message)
        else:
            await self.respond_to_human(message)

        return message

    async def respond_to_bot(self, message):
        """
        You should overwrite this method in your subclass with
        commands to issue when a bot sends a message in a channel
        that this bot has in it's authorized_channels property.
        :param message: Discord Message object
        :return: None by default, should be overwritten
        """

        return  # Overwrite me!

    async def respond_to_human(self, message):
        """
        You should overwrite this method in your subclass with
        commands to issue when a bot sends a message in a channel
        that this bot has in it's authorized_channels property.
        :param message: Discord Message object
        :return: None by default, should be overwritten
        """

        return  # Overwrite me!


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] %(message)s'
    )
    logging.getLogger('discord').setLevel(logging.WARNING)

    if (TOKEN := os.environ.get('TOKEN')) is None:
        raise ValueError("Please set the TOKEN environment variable.")

    authorized_channels = []  # Replace me

    bot = DiscordBot(channels=authorized_channels)
    bot.run(TOKEN)
