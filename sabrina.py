import logging
import os
import re
import time

from Assistant import DiscordBot
from constants import users
from constants.guilds import barrens_chat, trade_chat


class Sabrina(DiscordBot):
    def __init__(self, user_id=users.SABRINA, name="Sabrina", channels=None):
        super(Sabrina, self).__init__(user_id, name, channels)

    def _is_talking_to_me(self, msg, raw_mentions):
        return self._is_mentioned(self.name, msg, self.id, raw_mentions)

    def _is_seth_mentioned(self, msg, raw_mentions):
        name = 'seth'
        return self._is_mentioned(name, msg, users.SETH, raw_mentions)

    async def on_voice_state_update(self, member, before, after):
        if after.channel.id == barrens_chat.VOICE_CHILL_LOUNGE:
            if member.id == users.SOUMALY:
                general = self.channels[barrens_chat.TEXT_GENERAL]
                content = f"Here comes {member.mention} to steal MVP!"
                await general.send(content)

    async def on_message_delete(self, message):
        message, deleter, respond = await super().on_message_delete(message)
        if respond:
            resp = f"Good {deleter.mention}, hide the evidence..."
            await message.channel.send(resp, delete_after=3)

    async def respond_to_bot(self, message):
        content = None

        msg = message.content.casefold()

        # if 'hidden like mankrik\'s wife' in msg:
        #     content = "They must never know our secrets!"

        if content is not None:
            await message.channel.trigger_typing()
            time.sleep(1)
            await message.reply(content, delete_after=5)

    async def respond_to_human(self, message):
        msg = message.content.casefold()

        if self._is_talking_to_me(msg, message.raw_mentions):
            pattern = re.compile(
                r'hi|hello|greetings|hiya|hey|hola'
            )
            if re.search(pattern, msg):
                await message.reply(self.hello(message))

        if self._is_seth_mentioned(msg, message.raw_mentions):
            pattern = re.compile(
                r'how\s+do\s+(?:i|you)'
            )
            if re.search(pattern, msg):
                await message.reply(self.lmgt(msg))

    def hello(self, message):
        content = f"Hello {message.author.mention}."
        return content

    def lmgt(self, msg):
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
