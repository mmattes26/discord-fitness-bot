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

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import os
import json

# Load Google Sheets credentials from the environment variable
google_creds = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_NAME = "AI Fitness Bot Workouts"
sheet = client.open(SHEET_NAME).sheet1

@bot.command()
async def completeworkout(ctx, *, log: str):
    """Logs completed workouts in Google Sheets."""
    user = ctx.author.name
    today = datetime.today().strftime('%Y-%m-%d')

    # Parse the log format (e.g., "Squats ✅, Bench ❌, Rows ✅")
    exercises = log.split(", ")
    completed_exercises = []
    muscle_groups = set()

    for exercise in exercises:
        parts = exercise.split(" ")
        status = parts[-1]  # ✅ or ❌
        exercise_name = " ".join(parts[:-1])

        if status == "✅":
            completed_exercises.append(exercise_name)

        # Assign muscle groups based on exercise name
        muscle_group_mapping = {
            "squat": "Legs & Core",
            "bench": "Chest & Triceps",
            "row": "Back & Biceps",
            "press": "Shoulders",
            "plank": "Core"
        }
        for key, value in muscle_group_mapping.items():
            if key in exercise_name.lower():
                muscle_groups.add(value)

    # Convert muscle groups to a string
    muscle_groups_str = ", ".join(muscle_groups)

    # Log to Google Sheets
    sheet.append_row([today, user, muscle_groups_str, ", ".join(completed_exercises), "✅"])

    await ctx.send(f"✅ Workout logged! Trained muscle groups: {muscle_groups_str}")

# Run bot
bot.run(TOKEN)

