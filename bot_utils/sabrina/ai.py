import logging
import random
import re


import discord


class Searcher:
    def __init__(self, msg):
        self.msg = msg
        self.keywords = {
            'hello': self._hello(),
            'google': self._google(),
            'group_bots': self._group_bots()
        }

    def _search(self, regex, return_group=0):
        """
        Searches a string with a specified regular expression pattern.
        :param regex: Regular expression pattern
        :param return_group: Int number of a specific group to return
        :return: Regex search results group if found
        """

        result = None
        matches = re.search(regex, self.msg)
        if hasattr(matches, 'groups'):
            if return_group:
                result = matches.group(return_group)
            else:
                result = matches.groups()
        return result

    def _hello(self, regex=None):
        """
        Performs a regular expression search for a greeting.
        :param regex: Regular expression override
        :return: True if found
        """

        if regex is None:
            regex = re.compile(
                r'(hi|hello|greetings|hiya|hey|hola)\s', flags=re.IGNORECASE
            )
        hello = self._search(regex, 1)
        if hello is not None:
            hello = True
        return hello

    def _google(self, regex=None):
        """
        Performs a regular expression search for a greeting.
        :param regex: Regular expression override
        :return: True if found
        """

        if regex is None:
            regex = re.compile(
                r'((how\s+do\s+(?:i|you))|'
                r'(why\s+does\s+my)'
                r'.*)', flags=re.IGNORECASE
            )
        google = self._search(regex, 1)
        if google is not None:
            google = True
        return google

    def _group_bots(self, regex=None):
        """
        Performs a regular expression search for a command to move
        bots into dedicated roles.
        :param regex: Regular expression override
        :return: True if found
        """

        if regex is None:
            regex = re.compile(
                r'(group\s?(?:the)?\s?bots)\s?', flags=re.IGNORECASE
            )
        group_bots = self._search(regex, 1)
        if group_bots is not None:
            group_bots = True
        return group_bots

    def find_handlers(self):
        handler = Handler(self.keywords)
        return handler.find_handlers()


class Handler:
    def __init__(self, keywords):
        self.keywords = [k for k, v in keywords.items() if v is not None]
        logging.debug(f"KEYWORDS: {self.keywords}")

        # Handlers dict is composed of a Tuple of required keywords for
        # a key along with a list of handlers that can be triggered from
        # those keywords
        self.handlers = {
            ('hello',): self._say_hello,
            ('google',): self._lmgt,
            ('group_bots',): self._group_bots,
        }

    async def _create_role(self, ctx, message, callback=None):
        await ctx.fake_type(message.channel)
        await message.guild.create_role(name='Bots', hoist=True)
        if 'role' in message.content.casefold():  # A role was requested
            content = ctx._fstr(message, random.choice(ctx.complete_responses))
        else:
            content = f"I did not see a \"Bots\" role, so I made one for you."
        await message.reply(content)

    async def _lmgt(self, ctx, message, callback=None):
        lmgt = 'https://letmegooglethat.com'

        content = message.content

        if '?' in content:
            content = content.split('?')[0]

        regex = re.compile(
            r'((how\s+do\s+(?:i|you)|'
            r'(why\s+does\s+my))'
            r'.*)', flags=re.IGNORECASE
        )

        query_string = re.search(regex, content)

        query = re.sub(r'[^\w]+', '+', query_string.group(1))
        if query.endswith('+'):
            query = query[:-1]

        await ctx.fake_type(message.channel, seconds=2)
        await message.reply(f"{lmgt}/?q={query}")

    async def _say_hello(self, ctx, message, callback=None):
        await ctx.fake_type(message.channel)
        content = ctx._fstr(message, random.choice(ctx.greeting_responses))
        await message.reply(content)

    async def _group_bots(self, ctx, message, callback=None):
        await ctx.fake_type(message.channel)
        role = discord.utils.get(message.guild.roles, name='Bots')
        if role is None:
            await self._create_role(ctx, message, callback)
            role = discord.utils.get(message.guild.roles, name='Bots')
        async for member in message.guild.fetch_members():
            if member.bot:
                await member.add_roles(role)
        content = ctx._fstr(message, random.choice(ctx.complete_responses))
        await message.reply(content)

    def find_handlers(self):
        """
        Loops through the keywords to find any handlers that can be
        triggered.
        :return: List of handler Tuples
        """

        handlers = []
        for trigger_keywords, function in self.handlers.items():
            if all(keyword in self.keywords for keyword in trigger_keywords):
                handlers.append(function)
        return handlers
