# utils.py
import re
import os
import discord

URL_REGEX = re.compile(r'https?://')

def is_url(text: str) -> bool:
    return URL_REGEX.match(text) is not None

async def ensure_voice(interaction: discord.Interaction) -> discord.VoiceClient | None:
    vc = interaction.guild.voice_client
    if not vc:
        if interaction.user.voice:
            return await interaction.user.voice.channel.connect()
        else:
            await interaction.response.send_message("❌ You need to join a voice channel first!")
            return None
    return vc

def get_loop_after(vc, source_obj, *args, **kwargs):
    def after(error=None):
        if error:
            print(f"❗ Playback error: {error}")
        elif vc and vc.is_connected() and hasattr(source_obj, 'cleanup'):
            # On loop, clean up old process
            source_obj.cleanup()
            vc.play(source_obj, after=after)
    return after
