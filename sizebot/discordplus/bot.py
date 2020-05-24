from discord.ext.commands.bot import BotBase
import logging
from sizebot.lib import errors
from copy import copy

logger = logging.getLogger("sizebot")


async def process_commands(self, message):
    if message.author.bot:
        return

    contexts = []

    ctx = await self.get_context(message)

    if ctx.command and ctx.command.multiline:  # Command string starts with a multiline command, assume it's all one command
        contexts.append(ctx)
    elif not ctx.command:  # No command found, invoke will handle it
        contexts.append(ctx)
    else:
        lines = message.content.split("\n")
        for line in lines:
            newctx = copy(ctx)
            newctx.message.content = line
            contexts.append(newctx)

    for context in contexts:
        if ctx.command and ctx.command.multiline:  # This should only happen if they're the second arugment since we caught that earlier
            raise errors.MultilineAsNonFirstCommandException()

    for context in contexts:
        await self.invoke(context)


def patch():
    BotBase.process_commands = process_commands
