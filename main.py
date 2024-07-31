import logging
import os
import traceback

import discord
from discord import commands
from dotenv import load_dotenv

from cogs import EXTENSIONS


class TimeZoneLocalizer(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for cog in EXTENSIONS:
            try:
                await self.load_extension(f"{cog}")
            except commands.errors.ExtensionError:
                traceback.print_exc()


intents = discord.Intents(guilds=True, messages=True, message_content=True)

bot = TimeZoneLocalizer(
    command_prefix=commands.when_mentioned_or("t."),
    intents=intents,
    chunk_guilds_at_startup=False,
    strip_after_prefix=True,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
)


@bot.event
async def on_ready():
    print(bot.user)
    print(bot.user.id)


load_dotenv()
logging.basicConfig(level=logging.INFO)
bot.run(os.environ["TOKEN"])
