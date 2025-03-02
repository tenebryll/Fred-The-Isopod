import discord
from discord.ext import commands
token = "BOT-TOKEN"
owner = "OWNER_USERNAME"
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True
fred = commands.Bot(command_prefix = '~', intents = intents)
   
@fred.event
async def on_ready():
    print(f'{fred.user.name} is now Online!')

# Command for Fred to DM people ( ~msg @person hello )
@fred.command(name = "msg")
async def msg(ctx, user: discord.Member = None, *, message: str = None):
    if ctx.author.id != owner:
        return await ctx.send("You are not permitted to run this command")
    if not user:
        return await ctx.send("Specifiy a User")
    if not message:
        await ctx.send("Specify a Message")
    try:
        await user.send(message)
        await ctx.send(f"\"{message}\" sent to \"{user.mention}\"")
        def check(message):
            return message.author == user and message.channel.type == discord.ChannelType.private
        try:
            response = await fred.wait_for('message', timeout = 180, check = check)
            await ctx.send(f"Response from {user.mention}: {response.content}")
            await user.send("Awaiting your response..")
        except asyncio.TimeoutError:
            await ctx.send(f"No response from {user.mention}")
            await user.send("No response processed")
    except Exception as x:
       await ctx.send(f"Error: {x}")

# Command to have Fred talk in server (~say #general hello)
@fred.command(name = "say")
async def say(ctx, destination: discord.TextChannel = None, *, message: str = None):
    if ctx.author.id != owner:
        await ctx.send("You are not permitted to run this command")
        return
    if not destination:
        await ctx.send("Specify a TextChannel")
        return
    if not message:
        await ctx.send("Specify a Message")
        return
    try:
        await destination.send(message)
        await ctx.send(f"\"{message}\" sent to \"{destination.mention}\"")
    except Exception as x:
        await ctx.send(f"Error: {x}")

@fred.command(name = "log")
async def log(ctx):
    if ctx.author.name.id == owner:
        global log_channel
        log_channel = ctx.channel.id
        await ctx.send(f"Log channel set to {ctx.channel.mention}")
    else:
        await ctx.send("You are not permitted to run this command")

@fred.event
async def on_message_delete(message):
    if message.author.name != owner:
        embed = discord.Embed(title="{} deleted the message:".format(message.author.name), description="", color=0xFF0000)
        channel = fred.get_channel(log_channel)
        await channel.send(channel, embed=embed)

@fred.event
async def on_message_edit(message_before, message_after):
    if message_before.author.name != owner:
        embed = discord.Embed(title="{} edited a message".format(message_before.author.name), description="", color=0xFF0000)
        embed.add_field(name=message_before.content, value="Message before the edit", inline=True)
        embed.add_field(name=message_after.content, value="Message after the edit", inline=True)
        channel = fred.get_channel(log_channel)
        await channel.send(channel, embed=embed)

fred.run(token)
