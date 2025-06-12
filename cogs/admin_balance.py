import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_ROLE_NAME = "botDeveloper"  # 管理者判定用ロール名。必要に応じて変更してください。

def is_admin():
    async def predicate(interaction: discord.Interaction):
        # 管理者ロール保持を判定
        if interaction.user.guild is None:
            return False
        role = discord.utils.get(interaction.user.guild.roles, name=ADMIN_ROLE_NAME)
        return role in interaction.user.roles
    return app_commands.check(predicate)

class AdminBalance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_add", description="指定ユーザーの残高に+する（管理者限定）")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @is_admin()
    @app_commands.describe(user="対象ユーザー", amount="追加する金額")
    async def admin_add(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ 金額は正の数で指定してください", ephemeral=True)
            return
        user_id = str(user.id)
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id, balance, bank, win_rate) VALUES (?, 0, 0, 1.0)", (user_id,))
        cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"✅ {user.name}さんの残高に {amount}+ を追加しました。")

    @app_commands.command(name="admin_remove", description="指定ユーザーの残高から-する（管理者限定）")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @is_admin()
    @app_commands.describe(user="対象ユーザー", amount="減らす金額")
    async def admin_remove(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ 金額は正の数で指定してください", ephemeral=True)
            return
        user_id = str(user.id)
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row or row[0] < amount:
            conn.close()
            await interaction.response.send_message(f"❌ {user.name}さんの残高が不足しています。", ephemeral=True)
            return
        cur.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"✅ {user.name}さんの残高から {amount}+ を減らしました。")

    @app_commands.command(name="admin_check", description="指定ユーザーの残高を確認（管理者限定）")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @is_admin()
    @app_commands.describe(user="対象ユーザー")
    async def admin_check(self, interaction: discord.Interaction, user: discord.User):
        user_id = str(user.id)
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT balance, bank FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            await interaction.response.send_message(f"{user.name}さんの情報はありません。", ephemeral=True)
            return
        balance, bank = row
        embed = discord.Embed(title=f"{user.name}さんの通貨情報", color=discord.Color.blue())
        embed.add_field(name="所持金", value=f"{balance}+（プラ）")
        embed.add_field(name="金庫", value=f"{bank}+（プラ）")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminBalance(bot))
