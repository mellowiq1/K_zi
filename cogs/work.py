import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="work", description="働いてお金を稼ぐ")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def work(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        earned = random.randint(50, 200)

        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id, balance, bank, win_rate) VALUES (?, 0, 0, 1.0)", (user_id,))
        cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (earned, user_id))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"💼 働いて {earned}+（プラ）を稼ぎました！")

async def setup(bot):
    await bot.add_cog(Work(bot))
