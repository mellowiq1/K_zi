import discord
from discord.ext import commands
from discord import app_commands
import os

GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_ROLE_NAME = "BotDeveloper"

def is_owner():
    async def predicate(interaction: discord.Interaction):
        # サーバーオーナーのみ許可
        return interaction.user == interaction.guild.owner
    return app_commands.check(predicate)

class AdminManage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_add", description="管理者ロールを付与する（サーバーオーナー限定）")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @is_owner()
    @app_commands.describe(user="対象ユーザー")
    async def admin_add(self, interaction: discord.Interaction, user: discord.Member):
        role = discord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
        if not role:
            await interaction.response.send_message(f"❌ サーバーに「{ADMIN_ROLE_NAME}」ロールがありません。", ephemeral=True)
            return
        if role in user.roles:
            await interaction.response.send_message(f"⚠️ {user.display_name}さんはすでに管理者です。", ephemeral=True)
            return
        await user.add_roles(role)
        await interaction.response.send_message(f"✅ {user.display_name}さんに管理者ロールを付与しました。")

    @app_commands.command(name="admin_remove", description="管理者ロールを剥奪する（サーバーオーナー限定）")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @is_owner()
    @app_commands.describe(user="対象ユーザー")
    async def admin_remove(self, interaction: discord.Interaction, user: discord.Member):
        role = discord.utils.get(interaction.guild.roles, name=ADMIN_ROLE_NAME)
        if not role:
            await interaction.response.send_message(f"❌ サーバーに「{ADMIN_ROLE_NAME}」ロールがありません。", ephemeral=True)
            return
        if role not in user.roles:
            await interaction.response.send_message(f"⚠️ {user.display_name}さんは管理者ではありません。", ephemeral=True)
            return
        await user.remove_roles(role)
        await interaction.response.send_message(f"✅ {user.display_name}さんから管理者ロールを剥奪しました。")

async def setup(bot):
    await bot.add_cog(AdminManage(bot))
