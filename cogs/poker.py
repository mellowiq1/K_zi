import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3
import os
import asyncio

GUILD_ID = int(os.getenv("GUILD_ID"))

def deal_hand():
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['♠', '♥', '♦', '♣']
    deck = [v + s for v in values for s in suits]
    random.shuffle(deck)
    return [deck.pop() for _ in range(5)]

def evaluate_hand(hand):
    values = [card[:-1] for card in hand]
    pairs = [v for v in set(values) if values.count(v) == 2]
    if pairs:
        return "ワンペア", 1
    return "ノーペア", 0

class Poker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="poker", description="簡単なポーカーで遊ぶ")
    @app_commands.describe(bet="賭ける+の金額")
    async def poker(self, interaction: discord.Interaction, bet: int):
        if bet <= 0:
            await interaction.response.send_message("❌ 賭け金は1以上でなければなりません", ephemeral=True)
            return

        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT balance, win_rate FROM users WHERE user_id = ?", (str(interaction.user.id),))
        row = cur.fetchone()
        if not row or row[0] < bet:
            await interaction.response.send_message("❌ 残高が足りません", ephemeral=True)
            conn.close()
            return

        balance, win_rate = row
        hand = deal_hand()

        hand_display = " ".join(hand)
        embed = discord.Embed(
            title="🎴 ポーカー結果",
            description=f"**あなたの手札**: {hand_display}\n\n役を判定しています...",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

        # 3秒待って役判定を表示
        await asyncio.sleep(3)

        result, multiplier = evaluate_hand(hand)

        if multiplier > 0:
            reward = int(bet * (multiplier + win_rate))
            cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, str(interaction.user.id)))
            outcome_msg = f"🎉 {result}！{reward}+ を獲得しました！"
        else:
            cur.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bet, str(interaction.user.id)))
            outcome_msg = f"😞 {result}でした。{bet}+ を失いました。"

        conn.commit()
        conn.close()

        # 結果を編集して表示
        embed.description = f"**あなたの手札**: {hand_display}\n\n{outcome_msg}"
        await interaction.edit_original_response(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Poker(bot))
