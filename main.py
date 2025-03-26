import discord
from discord.ext import commands
from src.db import DB
from src.onlinefix import OnlineFix

from config import (
    BOT_TOKEN
)


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.all(), command_prefix="..")
        self.fix = OnlineFix()
        self.db = DB()

        self.games = list()

    async def on_ready(self) -> None:
        print("Ready")

    async def setup_hook(self) -> None:
        await self.load_extension("cogs.online")
        await self.load_extension("cogs.shop")

        await self.fix.start()

        await self.tree.sync()


client = Bot()

if __name__ == "__main__":
    client.run(BOT_TOKEN)
