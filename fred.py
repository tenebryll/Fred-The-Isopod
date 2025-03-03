import asyncio
import discord
from discord.ext import commands

token = "wadjaw9djaw9duqjdw9jdwjdqwjdqw"  # Replace with your actual token

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True

fred = commands.Bot(command_prefix='~', intents=intents)
log_channel = None  # Global log channel ID

@fred.event
async def on_ready():
    print(f'{fred.user.name} is now Online!')

@fred.command()
async def msg(ctx, user: discord.Member, *, message: str):
    """Sends a DM to a user and waits for a response."""
    if ctx.author.name not in ("mr_numbat", "cinnamon362"):
        return await ctx.send("You are not permitted to run this command")
    try:
        await user.send(message)
        await ctx.send(f'"{message}" sent to "{user.mention}"')
        try:
            response = await fred.wait_for('message', timeout=180, check=lambda m: m.author == user and m.channel.type == discord.ChannelType.private)
            await ctx.send(f'Response from {user.mention}: {response.content}')
            await user.send("Awaiting your response..")
        except asyncio.TimeoutError:
            await ctx.send(f'No response from {user.mention}')
            await user.send("No response processed")
    except Exception as e:
        await ctx.send(f'Error: {e}')

@msg.error
async def msg_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: ~msg <user> <message>", delete_after=5)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("User not found.", delete_after=5)
    else:
        await ctx.send(f"An error occurred: {error}", delete_after=5)

@fred.command()
async def say(ctx, destination: discord.TextChannel, *, message: str):
    """Sends a message to a specified text channel."""
    if ctx.author.name != "mr_numbat":
        return await ctx.send("You are not permitted to run this command")
    try:
        await destination.send(message)
        await ctx.send(f'"{message}" sent to "{destination.mention}"')
    except Exception as e:
        await ctx.send(f'Error: {e}')

@say.error
async def say_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: ~say <channel> <message>", delete_after=5)
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("Channel not found.", delete_after=5)
    else:
        await ctx.send(f"An error occurred: {error}", delete_after=5)

@fred.command(name="log", help="Sets where deleted and edited messages are sent.")
async def log(ctx):
    if ctx.author.name == "mr_numbat":
        global log_channel
        log_channel = ctx.channel.id
        await ctx.send(f"Log channel set to {ctx.channel.mention}", delete_after=True)
    else:
        await ctx.send("You are not permitted to run this command")

@fred.event
async def on_message_delete(message):
    """Logs deleted messages"""
    if message.author.name != "mr_numbat" and log_channel is not None:
        embed = discord.Embed(title=f"{message.author.name} deleted a message:", color=0xFF0000)
        channel = fred.get_channel(log_channel)
        if channel:
            await channel.send(embed=embed)

@fred.event
async def on_message_edit(message_before, message_after):
    """Logs edited messages"""
    if message_before.author.name != "mr_numbat" and log_channel is not None:
        embed = discord.Embed(title=f"{message_before.author.name} edited a message", color=0xFF0000)
        embed.add_field(name=message_before.content, value="Before", inline=False)
        embed.add_field(name=message_after.content, value="After", inline=False)
        channel = fred.get_channel(log_channel)
        if channel:
            await channel.send(embed=embed)

@fred.command(name="purge", help="[Admin] Mass delete messages.")
async def purge(ctx, limit: int):
    if ctx.author.guild_permissions.administrator:
        await ctx.message.delete()
        await asyncio.sleep(0.5)
        await ctx.channel.purge(limit=limit)
        embed = discord.Embed(title=f"Purged {limit} messages", description=f"Command executed by {ctx.author}.", color=0xFFEA00)
        await ctx.channel.send(embed=embed, delete_after=5)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: ~purge <limit>", delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You lack the required permissions", delete_after=5)
    else:
        await ctx.send(f"An error occurred: {error}", delete_after=5)

@fred.command(name="purge_user", help = "[Admin] Mass deletes messages from specified user.")
async def purge_user(ctx, user: discord.Member, limit: int):
    if ctx.author.guild_permissions.administrator:
        deleted = await ctx.channel.purge(limit=limit, check=lambda m: m.author == user)
        embed = discord.Embed(title=f"Purged {len(deleted)} messages from {user.mention}", description=f"Command executed by {ctx.author}.", color=0xFFEA00)
        await ctx.channel.send(embed=embed, delete_after=5)

@purge_user.error
async def purge_user_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: ~purge_user <user> <limit>", delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You lack the required permissions", delete_after=5)
    else:
        await ctx.send(f"An error occurred: {error}", delete_after=5)
fred.run(token)
