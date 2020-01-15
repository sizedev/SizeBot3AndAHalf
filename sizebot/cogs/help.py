import math
from datetime import datetime

import discord
from discord.ext import commands
from sizebot.discordplus import commandsplus

from sizebot import __version__
from sizebot import digilogger as logger
from sizebot import conf
from sizebot import userdb
from sizebot.digiSV import SV, WV
from sizebot.utils import chunkList, chunkLines

# name
# description
#     The message prefixed into the default help command.
# help = inspect.cleandoc(self.__doc__)
#     The long help text for the command.
# brief
#     The short help text for the command.
# short_doc = self.brief or help.split("\n")[0]
#     Gets the “short” documentation of a command.
# usage = ""
#     A replacement for arguments in the default help text.
# signature
#     Returns a POSIX-like signature useful for help command output.
# hidden = False
#     If True, the default help command does not show this in the help output.
# aliases = []


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commandsplus.command()
    async def units(self, ctx):
        """Get a list of the various units SizeBot accepts."""
        heightunits = [str(u) for u in sorted(SV._units)]
        weightunits = [str(u) for u in sorted(WV._units)]

        embed = discord.Embed(title=f"Units [SizeBot {__version__}]")

        for n, units in enumerate(chunkList(heightunits, math.ceil(len(heightunits) / 3))):
            embed.add_field(name="Height" if n == 0 else "\u200b", value="\n".join(units))

        for n, units in enumerate(chunkList(weightunits, math.ceil(len(weightunits) / 3))):
            embed.add_field(name="Weight" if n == 0 else "\u200b", value="\n".join(units))

        await ctx.send(embed=embed)

    async def send_summary_help(self, ctx):
        """Sends help summary.

        Help

        Commands

        {cmd.name} - {cmd.brief (or first line of cmd.help)}
        {cmd.name} - {cmd.brief (or first line of cmd.help)}
        ...
        """

        embed = discord.Embed(title=f"Help [SizeBot {__version__}]")

        commands = sorted((c for c in ctx.bot.commands if not c.hidden), key=lambda c: c.name)

        for n, fieldCommands in enumerate(chunkList(commands, math.ceil(len(commands) / 2))):
            fieldCommandsStr = "\n".join(f"**{c.name}**\n{c.summary or '-'}" for c in fieldCommands)
            embed.add_field(name="Commands" if n == 0 else "\u200b", value=fieldCommandsStr, inline=True)

        await ctx.send(embed=embed)

    async def send_command_help(self, ctx, cmd):
        """Sends help for a command.

        Help

        {prefix}{cmd.name} {cmd.usage (or autogenerated signature)}

        {cmd.description (optional)}

        {cmd.help (docstring, optional)}

        Aliases:
        alias1, alias2
        """
        signature = f"{ctx.prefix}{cmd.name} {cmd.signature}"

        descriptionParts = []
        if cmd.description:
            descriptionParts.append(cmd.description)
        if cmd.help:
            descriptionParts.append(cmd.help)
        description = "\n\n".join(descriptionParts)

        embed = discord.Embed(
            title=signature + f" [SizeBot {__version__}]",
            description=description
        ).set_author(name=f"Help")

        if cmd.aliases:
            embed.add_field(name="**Aliases:**", value=", ".join(cmd.aliases), inline=False)

        await ctx.send(embed=embed)

    @commandsplus.command(description="[description]", usage="[usage]", aliases=["helpme", "wtf"])
    async def help(self, ctx, cmdName: str = None):
        """[cmd.help[0]]

        [cmd.help[2]]
        [cmd.help[3]]
        """
        bot = ctx.bot
        if cmdName is None:
            await self.send_summary_help(ctx)
            return

        cmd = bot.all_commands.get(cmdName)
        if cmd:
            await self.send_command_help(ctx, cmd)
            return

        await ctx.send(f"Unrecognized command: {cmdName}")

    @commandsplus.command(
    )
    async def about(self, ctx):
        """Get the credits and some facts about SizeBot."""
        now = datetime.now()
        await ctx.send(
            "```\n"
            f"{conf.banner}\n"
            "```\n")
        await ctx.send(
            f"<@{ctx.message.author.id}>\n"
            "***SizeBot3½ by DigiDuncan***\n"
            "*A big program for big people.*\n"  # TODO: Change this slogan.
            "**Written for** *Size Matters*\n"
            "**Coding Assistance** *by Natalie*\n"
            "**Additional equations** *by Benyovski and Arceus3251*\n"
            "**Alpha Tested** *by AWK_*\n"
            "**Beta Tested** *by Kelly, worstgender, and Arceus3251.*\n"
            "**written in** *Python 3.7 with discord.py rewrite*\n"
            "**written with** *Atom* and *Visual Studio Code*\n"
            "**Special thanks** *to Reol, jyubari, and Memekip for making the Size Matters server, and Yukio and SpiderGnome for helping moderate it.*\n"
            "**Special thanks** *to the discord.py Community Discord for helping with code*\n"
            f"**Special thanks** *to the {userdb.count()} users of SizeBot3½.*\n"
            "\n"
            "\"She [*SizeBot*] is beautiful.\" -- *GoddessArete*\n"
            "\":100::thumbsup:\" -- *Anonymous*\n"
            "\"I want to put SizeBot in charge of the world government.\" -- *AWK*\n"
            "\"Um... I like it?\" -- *Goddess Syn*\n"
            "\"I am the only person who has accidentally turned my fetish into a tech support job.\" -- *DigiDuncan*\n"
            "\n"
            f"Version {__version__} | {now.strftime('%d %b %Y')}")

    @commandsplus.command()
    async def donate(self, ctx):
        """Give some monetary love to your favorite bot developer!"""
        await ctx.send(
            f"<@{ctx.message.author.id}>\n"
            "SizeBot is coded (mainly) and hosted by DigiDuncan, and for absolutely free.\n"
            "However, if you wish to contribute to DigiDuncan directly, you can do so here:\n"
            "https://ko-fi.com/DigiDuncan\n"
            "SizeBot has been a passion project coded over a period of three years and learning a lot of Python along the way.\n"
            "Thank you so much for being here throughout this journey!")

    @commandsplus.command(
        usage = "<message>"
    )
    async def bug(self, ctx, *, message: str):
        """Tell the devs there's an issue with SizeBot."""
        await logger.warn(f"{ctx.message.author.id} ({ctx.message.author.name}) sent a bug report.")
        await self.bot.get_user(conf.getId("DigiDuncan")).send(f"Bug report from <@{ctx.message.author.id}>: {message}")

        @commandsplus.command(
            usage = "<message>"
        )
        async def suggest(self, ctx, *, message: str):
            """Suggest a feature for SizeBot!"""
            await logger.warn(f"{ctx.message.author.id} ({ctx.message.author.name}) sent a bug report.")
            await self.bot.get_user(conf.getId("DigiDuncan")).send(f"Feature request from <@{ctx.message.author.id}>: {message}")

    @commandsplus.command()
    async def ping(self, ctx):
        """Pong!

        Check SizeBot's current latency."""
        await ctx.send('Pong! :ping_pong: {0}s'.format(round(self.bot.latency, 3)))


def setup(bot):
    bot.add_cog(HelpCog(bot))
