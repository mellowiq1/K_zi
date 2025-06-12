import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

class BankView(discord.ui.View):
    def __init__(self, user: discord.User, action: str, amount: int):
        super().__init__(timeout=60)
        self.user = user
        self.action = action
        self.amount = amount
        self.value = None  # 処理結果用

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # ボタンを押せるのはコマンド実行ユーザーのみ
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("これはあなたの操作ではありません。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="確定", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(self.user.id)

        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id, balance, bank, win_rate) VALUES (?, 0, 0, 1.0)", (user_id,))
        cur.execute("SELECT balance, bank FROM users WHERE user_id = ?", (user_id,))
        balance, bank = cur.fetchone()

        if self.action == "deposit":
            if balance < self.amount:
                await interaction.response.send_message("❌ 所持金が足りません", ephemeral=True)
                conn.close()
                self.stop()
                return
            cur.execute("UPDATE users SET balance = balance - ?, bank = bank + ? WHERE user_id = ?", (self.amount, self.amount, user_id))
            conn.commit()
            bank += self.amount
            await interaction.response.send_message(f"✅ {self.amount}+ を金庫に預けました。", ephemeral=True)

        elif self.action == "withdraw":
            if bank < self.amount:
                await interaction.response.send_message("❌ 金庫の残高が足りません", ephemeral=True)
                conn.close()
                self.stop()
                return
            cur.execute("UPDATE users SET balance = balance + ?, bank = bank - ? WHERE user_id = ?", (self.amount, self.amount, user_id))
            conn.commit()
            bank -= self.amount
            await interaction.response.send_message(f"✅ {self.amount}+ を金庫から引き出しました。", ephemeral=True)

        conn.close()

        # 処理後、金庫の残高を本人にだけ見える形で表示
        embed = discord.Embed(
            title="💰 あなたの金庫残高",
            description=f"現在の金庫残高は {bank}+ です。",
            color=discord.Color.gold()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

        self.stop()  # Viewを停止（ボタン無効化など）

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bank", description="所持金と金庫間でお金を移動する")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.choices(action=[
        app_commands.Choice(name="deposit", value="deposit"),
        app_commands.Choice(name="withdraw", value="withdraw"),
    ])
    @app_commands.describe(action="depositかwithdrawを選択", amount="移動させる金額")
    async def bank(self, interaction: discord.Interaction, action: app_commands.Choice[str], amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ 金額は正の数で指定してください", ephemeral=True)
            return

        view = BankView(interaction.user, action.value, amount)
        await interaction.response.send_message(
            f"アクション: **{action.name}**、金額: **{amount}+**\n確定ボタンを押してください。",
            view=view,
            ephemeral=True,
        )

async def setup(bot):
    await bot.add_cog(Bank(bot))
