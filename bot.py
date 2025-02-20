import discord
from discord.ext import commands
import openai
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the bot
bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this is set in your environment

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

@bot.command()
async def workout(ctx, *, user_input: str = None):
    """Handles natural language workout requests."""
    if not user_input:
        await ctx.send("Tell me what kind of workout you're looking for! Example: 'I want to build muscle, train chest & biceps for 45 minutes, and I'm an advanced lifter.'")
        return
    
    details = parse_workout_request(user_input)
    
    # If some details are missing, ask follow-ups
    missing_details = [key for key, value in details.items() if value is None]
    if missing_details:
        missing_str = ", ".join(missing_details)
        await ctx.send(f"I need more details! Can you clarify: {missing_str}?")
        return
    
    # Generate workout plan using OpenAI (updated API usage)
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a fitness coach that generates detailed workout plans."},
            {"role": "user", "content": f"Create a {details['goal']} workout focusing on {details['muscle_groups']}, lasting {details['length']}, for a {details['difficulty']} level lifter."}
        ]
    )
    
    workout_plan = response.choices[0].message.content
    
    # Send the generated workout
    await ctx.send(f"Here’s your personalized workout plan:\n{workout_plan}")

# Run bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
