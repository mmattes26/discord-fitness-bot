import openai
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token from .env file
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Enable required intents
intents = discord.Intents.default()
intents.message_content = True  # Required for commands to work

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

# Event: Bot successfully connected
@bot.event
async def on_ready():
    print(f'✅ Bot is online! Logged in as {bot.user}')

# Test command to check if bot responds
@bot.command()
async def test(ctx):
    await ctx.send("Bot is working!")

# AI Workout Generator Command
@bot.command()
async def workout(ctx, goal: str, type: str, length: str, equipment: str, difficulty: str):
    """Generates a personalized workout plan based on user preferences."""
    
    prompt = f"""
    Create a {length} workout plan focused on {goal}. 
    The workout should be a {type} routine using {equipment} and tailored for a {difficulty} fitness level.
    Include sets, reps, and rest times.
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a personal fitness trainer."},
            {"role": "user", "content": prompt}
        ]
    )
    
    await ctx.send(response.choices[0].message.content)

# Run bot
bot.run(TOKEN)

