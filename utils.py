# utils.py
import re
import discord

URL_REGEX = re.compile(r'https?://')

def is_url(text: str) -> bool:
    return URL_REGEX.match(text) is not None

# make sure we are connected to a voice channel
async def ensure_voice(interaction: discord.Interaction) -> discord.VoiceClient | None:
    vc = interaction.guild.voice_client
    if not vc:
        if interaction.user.voice:
            return await interaction.user.voice.channel.connect()
        else:
            await interaction.response.send_message("❌ Please join a voice channel first.")
            return None
    return vc

# loops the current song
def get_loop_after(vc: discord.VoiceClient, player_state, source_factory):
    def after(error=None):
        if error:
            print(f"❗ Playback error: {error}")
        elif player_state.is_looping:
            new_source = source_factory()
            player_state.current_source = new_source
            vc.play(new_source, after=after)
    return after
