import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from web.keep_alive import keep_alive
from db.init_db import create_users_table  # ← 追加

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        create_users_table()  # ← 最初にテーブル作成
        initial_cogs = ["cogs.economy", "cogs.blackjack", "cogs.poker", "cogs.admin", "cogs.admin_manage"]
        for cog in initial_cogs:
            await self.load_extension(cog)

        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

keep_alive()
bot.run(TOKEN)
