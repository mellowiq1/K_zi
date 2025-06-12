import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="お金の多いユーザーランキング")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def leaderboard(self, interaction: discord.Interaction):
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
        rows = cur.fetchall()
        conn.close()

        embed = discord.Embed(title="🏆 お金持ちランキング TOP10", color=discord.Color.green())
        for i, (user_id, balance) in enumerate(rows, start=1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(name=f"{i}位: {user.name}", value=f"{balance}+（プラ）", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
