import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
USER_ID = 1169487822344962060  # Specific user ID

# Enable message content intent
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True  # Add this line to enable message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

# Pagination class for server list
class PaginationView(View):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages
        self.current_page = 0

    @discord.ui.button(emoji='<:TWD_FIRST:1209075732676874340>', style=discord.ButtonStyle.secondary)
    async def first_page(self, button: Button, interaction: discord.Interaction):
        self.current_page = 0
        await self.update_message(interaction)

    @discord.ui.button(emoji='<:TWD_PREVIOUS:1298504437823967323>', style=discord.ButtonStyle.secondary)
    async def previous_page(self, button: Button, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_message(interaction)

    @discord.ui.button(emoji='<:TWD_NEXT:1298504381452517417>', style=discord.ButtonStyle.secondary)
    async def next_page(self, button: Button, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
        await self.update_message(interaction)

    @discord.ui.button(emoji='<a:TWD_CROSS:1183023325992202274>', style=discord.ButtonStyle.danger)
    async def delete(self, button: Button, interaction: discord.Interaction):
        await interaction.message.delete()

    async def update_message(self, interaction):
        embed = self.pages[self.current_page]
        await interaction.response.edit_message(embed=embed)

# Command to list servers
@bot.tree.command(name='servers')
async def servers(interaction: discord.Interaction):
    if interaction.user.id != USER_ID:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    guilds = bot.guilds
    embeds = []
    for i in range(0, len(guilds), 5):
        embed = discord.Embed(title="Servers", description="List of servers:")
        for guild in guilds[i:i + 5]:
            embed.add_field(name=guild.name, value=f"Link: {guild.vanity_url if guild.vanity_url else 'No link'}", inline=False)
        embeds.append(embed)

    view = PaginationView(embeds)
    await interaction.response.send_message(embed=embeds[0], view=view)

# Role management commands
async def manage_role(interaction, member, role_name, action):
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if not role:
        role = await interaction.guild.create_role(name=role_name)
        for channel in interaction.guild.channels:
            await channel.set_permissions(role, speak=False, send_messages=False)

    if action == 'add':
        await member.add_roles(role)
        await interaction.response.send_message(f"{member.display_name} has been muted.")
    elif action == 'remove':
        await member.remove_roles(role)
        await interaction.response.send_message(f"{member.display_name} has been unmuted.")

# Mute command
@bot.tree.command(name='mute')
async def mute(interaction: discord.Interaction, member: discord.Member):
    view = ConfirmationView(interaction, member, 'mute')
    embed = discord.Embed(title="Confirmation", description=f"Are you sure you want to mute {member.display_name}?")
    await interaction.response.send_message(embed=embed, view=view)

# Unmute command
@bot.tree.command(name='unmute')
async def unmute(interaction: discord.Interaction, member: discord.Member):
    view = ConfirmationView(interaction, member, 'unmute')
    embed = discord.Embed(title="Confirmation", description=f"Are you sure you want to unmute {member.display_name}?")
    await interaction.response.send_message(embed=embed, view=view)

# Kick command
@bot.tree.command(name='kick')
async def kick(interaction: discord.Interaction, member: discord.Member):
    view = ConfirmationView(interaction, member, 'kick')
    embed = discord.Embed(title="Confirmation", description=f"Are you sure you want to kick {member.display_name}?")
    await interaction.response.send_message(embed=embed, view=view)

# Ban command
@bot.tree.command(name='ban')
async def ban(interaction: discord.Interaction, member: discord.Member):
    view = ConfirmationView(interaction, member, 'ban')
    embed = discord.Embed(title="Confirmation", description=f"Are you sure you want to ban {member.display_name}?")
    await interaction.response.send_message(embed=embed, view=view)

# Confirmation view for role management commands
class ConfirmationView(View):
    def __init__(self, interaction, member, action):
        super().__init__()
        self.interaction = interaction
        self.member = member
        self.action = action

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: Button, interaction: discord.Interaction):
        if self.action == 'mute':
            await manage_role(interaction, self.member, 'Muted', 'add')
        elif self.action == 'unmute':
            await manage_role(interaction, self.member, 'Muted', 'remove')
        elif self.action == 'kick':
            await self.member.kick()
            await interaction.response.send_message(f"{self.member.display_name} has been kicked.")
        elif self.action == 'ban':
            await self.member.ban()
            await interaction.response.send_message(f"{self.member.display_name} has been banned.")
        await interaction.message.delete()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("Action cancelled.")
        await interaction.message.delete()

bot.run(TOKEN)