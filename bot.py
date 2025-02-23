import discord
from discord.ext import commands
import openai
import os
import re
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize the bot with required intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure this is enabled for command processing
bot = commands.Bot(command_prefix="/", intents=intents)

# Load OpenAI API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_creds = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client_gspread = gspread.authorize(creds)
sheet = client_gspread.open("AI Fitness Bot Workouts").sheet1

# User workout history storage
user_workout_history = {}

# Helper function to extract workout details from user input
def parse_workout_request(user_input):
    details = {
        "goal": None,
        "muscle_groups": None,
        "length": None,
        "difficulty": None
    }
    
    # Patterns to extract details
    goal_patterns = {
        "build muscle": "muscle gain",
        "lose fat": "fat loss",
        "increase endurance": "endurance",
        "strength training": "strength"
    }
    for key, value in goal_patterns.items():
        if key in user_input.lower():
            details["goal"] = value
    
    # Extract muscle groups
    muscle_match = re.search(r"(?:train|work on|do) ([\w\s]+)", user_input, re.IGNORECASE)
    if muscle_match:
        details["muscle_groups"] = muscle_match.group(1).strip()
    
    # Extract duration
    time_match = re.search(r"(\d{2,3})\s?(minutes|min|hours|hrs?)", user_input, re.IGNORECASE)
    if time_match:
        details["length"] = f"{time_match.group(1)}min"
    
    # Extract difficulty
    if "beginner" in user_input.lower():
        details["difficulty"] = "beginner"
    elif "intermediate" in user_input.lower():
        details["difficulty"] = "intermediate"
    elif "advanced" in user_input.lower():
        details["difficulty"] = "advanced"
    
    return details

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    user_input = message.content.lower()
    
    # Check for workout request in normal conversation
    if any(keyword in user_input for keyword in ["workout", "exercise", "train"]):
        details = parse_workout_request(user_input)
        
        missing_details = [key for key, value in details.items() if value is None]
        if missing_details:
            await message.channel.send(f"I need more details! Can you clarify: {', '.join(missing_details)}?")
            return
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fitness coach that generates detailed workout plans."},
                {"role": "user", "content": f"Create a {details['goal']} workout focusing on {details['muscle_groups']}, lasting {details['length']}, for a {details['difficulty']} level lifter."}
            ]
        )
        
        workout_plan = response.choices[0].message.content
        user_workout_history[message.author.id] = details  # Store user session
        
        await message.channel.send(f"Here’s your personalized workout plan:\n{workout_plan}")
    
    # Check for workout completion in normal conversation
    elif any(keyword in user_input for keyword in ["completed", "finished", "done with my workout"]):
        if message.author.id in user_workout_history:
            last_workout = user_workout_history[message.author.id]
            today = datetime.today().strftime('%Y-%m-%d')
            user = message.author.name
            muscle_groups = last_workout['muscle_groups']
            sheet.append_row([today, user, muscle_groups, "Completed", " "])
            await message.channel.send(f"✅ Workout logged! Trained muscle groups: {muscle_groups}")
        else:
            await message.channel.send("I don’t have a record of your last workout request. Can you tell me what you trained?")
    
    await bot.process_commands(message)

# Run bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
