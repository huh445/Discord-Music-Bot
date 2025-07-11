# bot.py
import discord
from discord.ext import commands

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    # Load your music cog and sync slash commands
    async def setup_hook(self):
        await self.load_extension("cogs.music")
        await self.tree.sync()

    async def on_ready(self):
        print(f"🤖 Logged in as {self.user} and ready.")
