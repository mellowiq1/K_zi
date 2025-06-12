import discord
from discord.ext import commands
from discord import app_commands
import random
import sqlite3
import os

GUILD_ID = int(os.getenv("GUILD_ID"))

def draw_card():
    cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    return random.choice(cards)

def calculate_hand(hand):
    value = 0
    aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']:
            value += 10
        elif card == 'A':
            value += 11
            aces += 1
        else:
            value += int(card)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

class BlackjackView(discord.ui.View):
    def __init__(self, user, bet, player_hand, dealer_hand):
        super().__init__()
        self.user = user
        self.bet = bet
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player_hand.append(draw_card())
        player_total = calculate_hand(self.player_hand)
        if player_total > 21:
            await interaction.response.defer()  # 先に応答保留
            await self.end_game(interaction, win=False, bust=True)
            self.disable_all_items()
        else:
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.blurple)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        while calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(draw_card())
        player_total = calculate_hand(self.player_hand)
        dealer_total = calculate_hand(self.dealer_hand)
        result = player_total > dealer_total or dealer_total > 21

        await interaction.response.defer()  # 先に応答保留
        await self.end_game(interaction, win=result)
        self.disable_all_items()
        await interaction.edit_original_response(embed=self.create_embed(), view=self)

    async def end_game(self, interaction, win, bust=False):
        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT win_rate FROM users WHERE user_id = ?", (str(self.user.id),))
        win_rate = cur.fetchone()
        if win_rate is None:
            win_rate = (1.0,)  # デフォルト倍率を1倍に
        win_rate = win_rate[0]

        if win:
            reward = int(self.bet * win_rate)
            cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, str(self.user.id)))
            result_text = f"🎉 勝ちました！{reward}+ を獲得しました。"
        else:
            cur.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (self.bet, str(self.user.id)))
            if bust:
                result_text = f"💥 バーストしました！{self.bet}+ を失いました。"
            else:
                result_text = f"😞 負けました。{self.bet}+ を失いました。"
        conn.commit()
        conn.close()

        # interaction.response はすでに defer しているので followup で送信
        await interaction.followup.send(result_text)

    def create_embed(self):
        return discord.Embed(
            title="🃏 ブラックジャック",
            description=f"**あなたの手札**: {', '.join(self.player_hand)} ({calculate_hand(self.player_hand)})\n"
                        f"**ディーラーの手札**: {', '.join(self.dealer_hand[:1])}, ❓",
            color=discord.Color.green()
        )

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="blackjack", description="ブラックジャックで遊ぶ")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(bet="賭ける+の金額")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        if bet <= 0:
            await interaction.response.send_message("❌ 賭け金は1以上でなければなりません", ephemeral=True)
            return

        conn = sqlite3.connect("db/users.db")
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (str(interaction.user.id),))
        row = cur.fetchone()
        conn.close()

        if row is None or row[0] < bet:
            await interaction.response.send_message("❌ 残高が足りません", ephemeral=True)
            return

        player_hand = [draw_card(), draw_card()]
        dealer_hand = [draw_card(), draw_card()]
        view = BlackjackView(interaction.user, bet, player_hand, dealer_hand)
        embed = view.create_embed()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
