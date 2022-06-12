import random

from constants import users
from constants.guilds import barrens_chat


DEFAULT_CHANNEL = barrens_chat.TEXT_GENERAL


async def joined_chill_lounge(ctx, member, before, after, channel=None):
    if channel is None:
        channel = ctx.channels[DEFAULT_CHANNEL]

    if member.id == users.SOUMALY:
        await ctx.fake_type(channel, 2)
        content = f"Here comes {member.mention} to steal MVP!"
        await channel.send(content, delete_after=10)


async def joined_voice_chat(ctx, member, before, after, channel=None):
    if channel is None:
        channel = ctx.channels[DEFAULT_CHANNEL]

    channel_members = after.channel.voice_states.keys()
    num = ctx._num_members(channel_members, users.ALL_REAL_USERS)
    if num > 4:
        await ctx.fake_type(channel, 2)
        content = "Holy shit, the gang's all here!"
        await channel.send(content, delete_after=10)
    elif num > 3:
        await ctx.fake_type(channel, 2)
        content = f"Hey look, even {member.mention} is on."
        await channel.send(content, delete_after=10)


async def message_deleted(ctx, message, deleter):
    channel = message.channel
    await ctx.fake_type(channel)
    resp = f"Good {deleter.mention}, hide the evidence..."
    await channel.send(resp, delete_after=10)


async def bot_routine(ctx, message):
    msg = message.content.casefold()

    if 'do a better job' in msg:  # CrossRoads Bot
        await ctx.fake_type(message.channel)
        content = ctx._fstr(random.choice(ctx.negative_responses))
        await message.reply(content, delete_after=5)

    elif 'going to play Heroes' in msg:  # CrossRoads Bot
        await ctx.fake_type(message.channel)
        if users.SOUMALY in message.channel.members:
            soumaly = await ctx.fetch_user(users.SOUMALY)
            content = f"I wonder who MVP will be..." \
                      f"*cough*{soumaly.mention}*cough*"
        else:
            content = "Looks like a possible game night to me!"
        await message.reply(content, delete_after=5)
