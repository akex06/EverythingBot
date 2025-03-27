import dataclasses

import discord
from discord import app_commands
from discord.ext import commands, tasks

from main import Bot


@dataclasses.dataclass
class Game:
    name: str
    url: str


async def game_autocomplete(
        interaction: discord.Interaction,
        current: str
) -> list[app_commands.Choice[str]]:
    games = interaction.client.games

    return [
               app_commands.Choice(name=game.name, value=game.url)
               for game in games if current.casefold() in game.name.casefold()
           ][:25]


async def get_games(bot: Bot) -> list[Game]:
    games = list()
    async for page in bot.fix.get_pages("https://online-fix.me/"):
        for article in page.find("div", {"class": "news-container"}).find_all("article", {"class": "news"}):
            game_url = article.find("a", {"class": "big-link"})["href"].removeprefix("https://online-fix.me")
            game_title = article.find("div", {"class": "article-content"}).find("h2", {"class": "title"}).text.strip()
            games.append(Game(game_title, game_url))

    return games


class Online(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.update_games.start()

    @tasks.loop(minutes=30)
    async def update_games(self):
        print("Starting caching games")
        self.bot.games = sorted(await get_games(self.bot), key=lambda game: game.name.casefold())
        print("Finished caching games")

    @commands.hybrid_command(
        name="download",
        with_app_command=True
    )
    @app_commands.autocomplete(url=game_autocomplete)
    async def download(self, ctx: commands.Context, url: str) -> None:
        try:
            file = await self.bot.fix.download_game(f"https://online-fix.me{url}")
            await ctx.reply(
                "Paga el juego zorra",
                file=file
            )
        except TypeError:
            await ctx.reply("Ese juego no tiene un torrent")


async def setup(bot: Bot) -> None:
    await bot.add_cog(Online(bot))
