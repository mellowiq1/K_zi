# casino_bot/cogs/admin.py
import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_ROLE_NAME = "BotDeveloper"

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("db/users.db")
        self.cur = self.conn.cursor()

    def is_admin(self, member: discord.Member):
        return any(role.name == ADMIN_ROLE_NAME for role in member.roles)

    @app_commands.command(name="add_money", description="指定ユーザーに+を追加")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def add_money(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if not self.is_admin(interaction.user):
            return await interaction.response.send_message("❌ 管理者専用コマンドです。", ephemeral=True)
        self.cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user.id,))
        self.cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user.id))
        self.conn.commit()
        await interaction.response.send_message(f"✅ {user.name} に {amount}+ を追加しました。")

    @app_commands.command(name="remove_money", description="指定ユーザーから+を減らす")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def remove_money(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if not self.is_admin(interaction.user):
            return await interaction.response.send_message("❌ 管理者専用コマンドです。", ephemeral=True)
        self.cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user.id,))
        self.cur.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user.id))
        self.conn.commit()
        await interaction.response.send_message(f"✅ {user.name} から {amount}+ を削除しました。")

    @app_commands.command(name="check_balance", description="指定ユーザーの残高を確認")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def check_balance(self, interaction: discord.Interaction, user: discord.User):
        if not self.is_admin(interaction.user):
            return await interaction.response.send_message("❌ 管理者専用コマンドです。", ephemeral=True)
        self.cur.execute("SELECT balance, bank FROM users WHERE user_id = ?", (user.id,))
        result = self.cur.fetchone()
        if result:
            balance, bank = result
            await interaction.response.send_message(f"{user.name} の残高: {balance}+（プラ）\n金庫: {bank}+（プラ）")
        else:
            await interaction.response.send_message(f"{user.name} はまだデータがありません。")

async def setup(bot):
    await bot.add_cog(Admin(bot))
