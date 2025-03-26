from io import BytesIO

import discord
import numpy as np
import requests
from discord import app_commands
from discord.ext import commands
from PIL import Image
from src.valorant import Valorant

AUTH_URL = "https://auth.riotgames.com/authorize?redirect_uri=http://localhost/redirect&client_id=riot-client&response_type=token%20id_token&nonce=1&scope=openid%20link%20ban%20lol_region%20account"


def get_average_color(url: str) -> int:
    image = Image.open(BytesIO(requests.get(url).content))
    image = image.convert("RGB")

    pixels = np.array(image)
    avg_color = np.mean(pixels, axis=(0, 1))

    color = tuple(avg_color.astype(int))
    int_color = 0
    for c in color:
        int_color <<= 8
        int_color += c

    return int(int_color)


async def send_store(interaction: discord.Interaction, user_id: int = None, access_token: str = None) -> None:
    if user_id is None:
        user_id = interaction.user.id

    if access_token is None:
        access_token = interaction.client.db.get_access_token(user_id)
    val = Valorant(access_token)

    embeds = list()
    for store_skin in val.get_store_skins():
        skin_id = store_skin["OfferID"]
        skin = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}").json()["data"]

        image_url = skin["displayIcon"]

        embed = discord.Embed(
            description=f"{store_skin["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]}VP",
            color=get_average_color(image_url)
        )

        embed.set_image(url=image_url)
        embed.set_author(name=skin["displayName"], url=skin["streamedVideo"])

        embeds.append(embed)

    await interaction.channel.send(f"Tienda de <@{user_id}>", embeds=embeds)


async def send_all_stores(interaction: discord.Interaction) -> None:
    for user_id, access_token in interaction.client.db.get_all():
        try:
            await send_store(interaction, user_id)
        except ValueError:
            interaction.client.db.remove_access_token(user_id)
            print(f"Removing {user_id} due to access token being not valid")


class AccessTokenModal(discord.ui.Modal, title="Código de Verificación"):
    url = discord.ui.TextInput(label="URL")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        access_token = self.url.value.split("#")[1].split("=")[1].split("&")[0]

        interaction.client.db.set_access_token(interaction.user.id, access_token)
        await interaction.response.send_message("Código introducido correctamente")


class NoAccessTokenView(discord.ui.View):
    @discord.ui.button(label="Generar código")
    async def generar(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(AccessTokenModal())


class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="reload")
    async def reload(self, ctx: commands.Context) -> None:
        await ctx.bot.reload_extension("cogs.shop")
        await ctx.reply("Reloaded!")

    @app_commands.command(name="tienda")
    async def tienda(self, interaction: discord.Interaction):
        try:
            await send_store(interaction)
        except ValueError:
            embed = discord.Embed(
                title="Código de verificación expirado",
                description=f"Para generar un nuevo código de verificación accede [aquí]({AUTH_URL})"
                            f", una vez iniciada sesión (no aparecerá ninguna web) copia el enlace "
                            f"y dale al botón de introducir código",
                color=0xFF00FF
            )
            await interaction.response.send_message(embed=embed, view=NoAccessTokenView())

    @app_commands.command(name="sendall")
    async def sendall(self, interaction: discord.Interaction) -> None:
        await send_all_stores(interaction)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shop(bot))
