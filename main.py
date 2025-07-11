# main.py
import os
from dotenv import load_dotenv
from bot import MusicBot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("Discord token not found. Please set DISCORD_TOKEN in .env")

bot = MusicBot()
bot.run(TOKEN)
