from dotenv import load_dotenv
import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask, render_template
import traceback

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Enable necessary intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize Discord bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask app setup
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/commands')
def commands_page():
    return render_template('commands.html')

# Pagination classes
class PaginationView(discord.ui.View):
    def __init__(self, pages: list[str], *, interaction: discord.Interaction):
        super().__init__()
        self.pages = pages
        self.current_page = 0
        self.interaction = interaction
        self.update_buttons()

    def update_buttons(self):
        self.go_to_first_page.disabled = self.current_page == 0
        self.go_to_previous_page.disabled = self.current_page == 0
        self.go_to_next_page.disabled = self.current_page >= len(self.pages) - 1
        self.go_to_last_page.disabled = self.current_page >= len(self.pages) - 1

    async def show_page(self):
        await self.interaction.response.edit_message(content=self.pages[self.current_page], view=self)

    @discord.ui.button(label="First", style=discord.ButtonStyle.blurple)
    async def go_to_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        await self.show_page()

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def go_to_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.show_page()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def go_to_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.show_page()

    @discord.ui.button(label="Last", style=discord.ButtonStyle.blurple)
    async def go_to_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = len(self.pages) - 1
        await self.show_page()

# Mute role creation function
async def get_or_create_muted_role(guild):
    role = discord.utils.get(guild.roles, name="Muted")
    if not role:
        role = await guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False, connect=False, add_reactions=False))
    return role

# Mute command
@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    muted_role = await get_or_create_muted_role(ctx.guild)
    await member.add_roles(muted_role)
    await ctx.send(f"{member.mention} has been muted successfully.")

# Unmute command
@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} has been unmuted successfully.")
    else:
        await ctx.send(f"{member.mention} is not muted.")

# Kick command
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked from the server.")

# Ban command
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned from the server.")

# Unban command
@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned_users = await ctx.guild.bans()
    member_name , member_discriminator = member_name.split('#')
    for ban in banned_users:
        user = ban.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} has been unbanned from the server.")
            return
    await ctx.send(f"User not found.")

# Timeout command
@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: int):
    await member.timeout(duration=discord.utils.utcnow() + discord.timedelta(minutes=duration))
    await ctx.send(f"{member.mention} has been timed out for {duration} minutes.")

# Untimeout command
@bot.command(name='untimeout')
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    await member.timeout(duration=None)
    await ctx.send(f"{member.mention} has been untimeouted.")

# Servers command
@bot.command(name='servers')
async def servers_command(ctx):
    if ctx.author.id != 1169487822344962060:  # Check if the user is the owner
        await ctx.send("You do not have permission to use this command.")
        return  # Ignore the command without response

    guilds_data = []
    
    # Iterate through all guilds the bot is a member of
    for guild in bot.guilds:
        invites = await guild.invites()
        invite_link = invites[0].url if invites else "No invite available"
        guilds_data.append(f"{guild.name}: {invite_link}")  # Store guild and its invite link

    if not guilds_data:
        await ctx.send("No guilds found.")
        return

    # Create a pagination view and start it
    view = PaginationView(guilds_data, interaction=ctx)
    await ctx.send(content=guilds_data[0], view=view)

# Application commands
@bot.tree.command(name="mute", description="Mute a member")
@commands.has_permissions(manage_roles=True)
async def mute_app_command(interaction: discord.Interaction, member: discord.Member):
    muted_role = await get_or_create_muted_role(interaction.guild)
    await member.add_roles(muted_role)
    await interaction.response.send_message(f"{member.mention} has been muted successfully.")

@bot.tree.command(name="unmute", description="Unmute a member")
@commands.has_permissions(manage_roles=True)
async def unmute_app_command(interaction: discord.Interaction, member: discord.Member):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await interaction.response.send_message(f"{member.mention} has been unmuted successfully.")
    else:
        await interaction.response.send_message(f"{member.mention} is not muted.")

@bot.tree.command(name="kick", description="Kick a member")
@commands.has_permissions(kick_members=True)
async def kick_app_command(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been kicked from the server.")

@bot.tree.command(name="ban", description="Ban a member")
@commands.has_permissions(ban_members=True)
async def ban_app_command(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been banned from the server.")

@bot.tree.command(name="unban", description="Unban a member")
@commands.has_permissions(ban_members=True)
async def unban_app_command(interaction: discord.Interaction, member_name: str):
    banned_users = await interaction.guild.bans()
    member_name, member_discriminator = member_name.split('#')
    for ban in banned_users:
        user = ban.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"{user.mention} has been unbanned from the server.")
            return
    await interaction.response.send_message(f"User not found.")

@bot.tree.command(name="timeout", description="Timeout a member")
@commands.has_permissions(moderate_members=True)
async def timeout_app_command(interaction: discord.Interaction, member: discord.Member, duration: int):
    await member.timeout(duration=discord.utils.utcnow() + discord.timedelta(minutes=duration))
    await interaction.response.send_message(f"{member.mention} has been timed out for {duration} minutes.")

@bot.tree.command(name="untimeout", description="Untimeout a member")
@commands.has_permissions(moderate_members=True)
async def untimeout_app_command(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(duration=None)
    await interaction.response.send_message(f"{member.mention} has been untimeouted.")

# Run Flask app in a separate thread
def run_app():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_app).start()

# Run Discord bot
bot.run(TOKEN)