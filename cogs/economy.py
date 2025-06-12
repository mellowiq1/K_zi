import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user(self, user_id):
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (str(user_id),))
        conn.commit()
        cur.execute("SELECT balance, bank FROM users WHERE user_id = ?", (str(user_id),))
        data = cur.fetchone()
        conn.close()
        return data

    @app_commands.command(name="work", description="働いて+を稼ぎます")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def work(self, interaction: discord.Interaction):
        import random
        amount = random.randint(10, 100)
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (str(interaction.user.id),))
        cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, str(interaction.user.id)))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"💼 あなたは働いて **{amount}+** を稼ぎました！")

    @app_commands.command(name="balance", description="あなたの残高と金庫残高を表示します")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def balance(self, interaction: discord.Interaction):
        balance, bank = self.get_user(interaction.user.id)
        await interaction.response.send_message(f"💰 残高: {balance}+　｜　🪙 金庫: {bank}+")

    @app_commands.command(name="bank", description="残高と金庫の間でお金を移動します")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(direction="in → 金庫に入れる, out → 金庫から出す", amount="移動金額")
    async def bank(self, interaction: discord.Interaction, direction: str, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ 金額は正の数である必要があります", ephemeral=True)
            return

        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT balance, bank FROM users WHERE user_id = ?", (str(interaction.user.id),))
        balance, bank = cur.fetchone()

        if direction == "in":
            if amount > balance:
                await interaction.response.send_message("❌ 残高が足りません", ephemeral=True)
                return
            cur.execute("UPDATE users SET balance = balance - ?, bank = bank + ? WHERE user_id = ?", (amount, amount, str(interaction.user.id)))
            conn.commit()
            await interaction.response.send_message(f"📥 金庫に **{amount}+** を預けました")
        elif direction == "out":
            if amount > bank:
                await interaction.response.send_message("❌ 金庫の金額が足りません", ephemeral=True)
                return
            cur.execute("UPDATE users SET balance = balance + ?, bank = bank - ? WHERE user_id = ?", (amount, amount, str(interaction.user.id)))
            conn.commit()
            await interaction.response.send_message(f"📤 金庫から **{amount}+** を引き出しました")
        else:
            await interaction.response.send_message("❌ `in` または `out` を指定してください", ephemeral=True)

        conn.close()

    @app_commands.command(name="leaderboard", description="通貨の所持金でサーバー内ランキングを表示します")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def leaderboard(self, interaction: discord.Interaction):
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT user_id, balance + bank AS total FROM users ORDER BY total DESC LIMIT 10")
        rows = cur.fetchall()
        conn.close()

        embed = discord.Embed(title="🏆 通貨ランキング", color=discord.Color.gold())
        for i, (uid, total) in enumerate(rows):
            user = await self.bot.fetch_user(int(uid))
            embed.add_field(name=f"{i+1}. {user.display_name}", value=f"{total}+", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
