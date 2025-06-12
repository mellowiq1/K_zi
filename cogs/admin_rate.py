import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_ROLE_NAME = "BotDeveloper"

def is_admin():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild is None:
            return False
        role = discord.utils.get(interaction.user.guild.roles, name=ADMIN_ROLE_NAME)
        return role in interaction.user.roles
    return app_commands.check(predicate)

class AdminRate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_winrate", description="指定ユーザーの勝率倍率を変更する（管理者限定）")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @is_admin()
    @app_commands.describe(user="対象ユーザー", rate="倍率（例: 1.0=通常, 2.0=2倍）")
    async def set_winrate(self, interaction: discord.Interaction, user: discord.User, rate: float):
        if rate <= 0:
            await interaction.response.send_message("❌ 倍率は正の数で指定してください", ephemeral=True)
            return
        user_id = str(user.id)
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id, balance, bank, win_rate) VALUES (?, 0, 0, 1.0)", (user_id,))
        cur.execute("UPDATE users SET win_rate = ? WHERE user_id = ?", (rate, user_id))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"✅ {user.name}さんの勝率倍率を {rate} 倍に設定しました。")

    async def cog_load(self):
        guild = discord.Object(id=GUILD_ID)
        self.bot.tree.add_command(self.set_winrate, guild=guild)
        await self.bot.tree.sync(guild=guild)

async def setup(bot):
    await bot.add_cog(AdminRate(bot))
