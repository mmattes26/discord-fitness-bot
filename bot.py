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
async def workout(ctx, goal: str = "general", muscle_groups: str = None, length: str = "45min", equipment: str = "bodyweight", difficulty: str = "beginner"):
    """Suggests a workout based on past trends or generates a new one."""
    user = ctx.author.name
    today = datetime.today().strftime('%A')  # Get current day of the week

    # Retrieve past workouts from Google Sheets
    history = sheet.get_all_records()

    # Find user's workout trends
    user_workouts = [row for row in history if row["User"] == user]
    recent_workouts = user_workouts[-5:]  # Get last 5 workouts

    muscle_history = {}  # Track muscle groups trained on different days

    for workout in recent_workouts:
        if workout["Muscle Groups"] not in muscle_history:
            muscle_history[workout["Day"]] = workout["Muscle Groups"]

    # Check if a trend exists for today
    if today in muscle_history:
        suggested_muscles = muscle_history[today]
        await ctx.send(f"📅 You typically train **{suggested_muscles}** on {today}s. Would you like to do that today? (Yes/No)")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

        try:
            msg = await bot.wait_for("message", check=check, timeout=30)  # Wait for user response
            if msg.content.lower() == "yes":
                muscle_groups = suggested_muscles
            else:
                await ctx.send("👍 No problem! Generating a fresh workout...")
        except asyncio.TimeoutError:
            await ctx.send("⏳ No response detected, generating a new workout!")

    # Generate workout (same logic as before)
    workout_plan = f"1️⃣ Squats - 4 sets x 8 reps\n2️⃣ Push-ups - 3 sets x 12 reps\n..."  # Replace with AI generation
    await ctx.send(f"💪 Here’s your workout for today:\n{workout_plan}")

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

