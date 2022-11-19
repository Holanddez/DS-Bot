import discord
from discord.ext import commands
from discord import File
from easy_pil import Editor, load_image_async, Font
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')

intents = discord.Intents().default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is alive! {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.system_channel
    background = Editor("imgs\\neon-anime.jpg")

    profile_pic = await load_image_async(str(member.avatar.url))
    profile = Editor(profile_pic).resize((250, 250)).circle_image()

    poppins = Font.poppins(variant='bold', size=50)
    small_poppins = Font.poppins(variant='regular', size=20)

    background.paste(profile, (320, 80))
    background.ellipse((320, 80), 250, 250, outline='white', stroke_width=5)

    background.text((450, 360), f"Welcome to {member.guild.name}", color="white", font=poppins, align="center")
    background.text((450, 425), f"{member.name}#{member.discriminator}", color="white", font=small_poppins, align="center")

    file = File(fp=background.image_bytes, filename="welcome.jpg")

    await channel.send(f"Hello {member.mention}! Welcome to **{member.guild.name}**")
    await channel.send(file=file)

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.channel.send(f"Successfully loaded {extension}!")

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.channel.send(f"Successfully unloaded {extension}!")

@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')
    await ctx.channel.send(f"Successfully reloaded {extension}!")

for file in os.listdir('./cogs'):
    if file.endswith('.py'):
        bot.load_extension(f'cogs.{file[:-3]}')

bot.run(TOKEN)