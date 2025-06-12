import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="あなたの所持金と金庫を確認します")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def balance(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT balance, bank FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            balance, bank = row
        else:
            balance, bank = 0, 0

        embed = discord.Embed(
            title=f"💳 {interaction.user.name}の残高",
            description=f"💵 所持金: {balance}+\n🏦 金庫: {bank}+",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Balance(bot))
