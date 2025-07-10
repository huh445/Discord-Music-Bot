import re
import os
import asyncio
import discord
from discord import app_commands
import yt_dlp

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

URL_REGEX = re.compile(r'https?://')

# yt-dlp and ffmpeg setup
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'source_address': '0.0.0.0',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


# Global state wrapper
class PlayerState:
    current_playlist = []
    current_folder = None
    current_song = None
    is_looping = False


# Helpers
def is_url(text: str) -> bool:
    return URL_REGEX.match(text) is not None


async def ensure_voice(interaction: discord.Interaction) -> discord.VoiceClient | None:
    vc = interaction.guild.voice_client
    if not vc:
        if interaction.user.voice:
            return await interaction.user.voice.channel.connect()
        else:
            await interaction.response.send_message("❌ You're not in a voice channel!")
            return None
    return vc


def get_loop_after(vc, source_func, *args, **kwargs):
    def after(error=None):
        if error:
            print(f"❗ Playback error: {error}")
        elif PlayerState.is_looping:
            vc.play(source_func(*args, **kwargs), after=after)
    return after


# Slash Commands
@tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        await interaction.user.voice.channel.connect()
        await interaction.response.send_message("✅ Joined voice channel!")
    else:
        await interaction.response.send_message("❌ You're not in a voice channel!")


@tree.command(name="leave", description="Leave the current voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 Disconnected!")
    else:
        await interaction.response.send_message("❌ I'm not in a voice channel!")


@tree.command(name="play", description="Search and play a song from YouTube")
@app_commands.describe(search="Song name or YouTube URL")
async def play(interaction: discord.Interaction, search: str):
    vc = await ensure_voice(interaction)
    if not vc: return

    await interaction.response.send_message(f"🔍 Searching for: `{search}`")
    try:
        query = search if is_url(search) else f"ytsearch:{search}"
        data = ytdl.extract_info(query, download=False)

        if 'entries' in data:
            data = data['entries'][0]

        url = data['url']
        PlayerState.current_song = data.get('title', 'Unknown Title')

        vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options),
                after=get_loop_after(vc, discord.FFmpegPCMAudio, url, **ffmpeg_options))

        await interaction.followup.send(f"🎶 Now playing: **{PlayerState.current_song}**")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}")


@tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message(f"⏭️ Skipped **{PlayerState.current_song}**")
    else:
        await interaction.response.send_message("❌ Nothing is playing.")


@tree.command(name="nowplaying", description="Show the current song")
async def nowplaying(interaction: discord.Interaction):
    song = PlayerState.current_song
    if song:
        await interaction.response.send_message(f"🎧 Now playing: **{song}**")
    else:
        await interaction.response.send_message("❌ No song is currently playing.")


@tree.command(name="play_url", description="Play a YouTube audio stream from a URL")
@app_commands.describe(url="Direct YouTube URL")
async def play_url(interaction: discord.Interaction, url: str):
    vc = await ensure_voice(interaction)
    if not vc: return

    await interaction.response.send_message("🔗 Loading...")

    try:
        data = ytdl.extract_info(url, download=False)
        if 'entries' in data:
            data = data['entries'][0]

        stream_url = data['url']
        PlayerState.current_song = data.get('title', 'Unknown Title')

        vc.stop()
        vc.play(discord.FFmpegPCMAudio(stream_url, **ffmpeg_options),
                after=get_loop_after(vc, discord.FFmpegPCMAudio, stream_url, **ffmpeg_options))

        await interaction.followup.send(f"🎧 Streaming: **{PlayerState.current_song}**")

    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}")


@tree.command(name="play_mp3", description="Play a local MP3 from /songs")
@app_commands.describe(filename="The name of the file in /songs")
async def play_mp3(interaction: discord.Interaction, filename: str):
    vc = await ensure_voice(interaction)
    if not vc: return

    path = os.path.join("songs", filename)
    if not os.path.isfile(path):
        await interaction.response.send_message(f"❌ File `{filename}` not found in `/songs`.")
        return

    PlayerState.current_song = filename
    vc.play(discord.FFmpegPCMAudio(path),
            after=get_loop_after(vc, discord.FFmpegPCMAudio, path))

    await interaction.response.send_message(f"🎵 Playing local file: **{filename}**")


@tree.command(name="play_playlist", description="Play a folder of MP3s as a playlist")
@app_commands.describe(playlist_name="Name of the folder in /playlist")
async def play_playlist(interaction: discord.Interaction, playlist_name: str):
    vc = await ensure_voice(interaction)
    if not vc: return

    folder_path = os.path.join("playlist", playlist_name)
    if not os.path.isdir(folder_path):
        await interaction.response.send_message(f"❌ Playlist `{playlist_name}` not found.")
        return

    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".mp3")])
    if not files:
        await interaction.response.send_message("❌ No MP3s found.")
        return

    PlayerState.current_playlist = files.copy()
    PlayerState.current_folder = folder_path
    PlayerState.current_song = PlayerState.current_playlist.pop(0)

    await interaction.response.send_message(
        f"📻 Playing `{playlist_name}` starting with **{PlayerState.current_song}**")

    text_channel = interaction.channel

    def play_next(error=None):
        if error:
            print(f"❗ Playback error: {error}")
            return

        if PlayerState.current_playlist:
            PlayerState.current_song = PlayerState.current_playlist.pop(0)
            full_path = os.path.join(PlayerState.current_folder, PlayerState.current_song)

            coro = text_channel.send(f"▶️ Now playing: **{PlayerState.current_song}**")
            asyncio.run_coroutine_threadsafe(coro, client.loop)

            vc.play(discord.FFmpegPCMAudio(full_path), after=play_next)
        else:
            coro = text_channel.send("✅ Playlist finished.")
            asyncio.run_coroutine_threadsafe(coro, client.loop)
            PlayerState.current_song = None
            PlayerState.current_playlist.clear()
            PlayerState.current_folder = None

    full_path = os.path.join(PlayerState.current_folder, PlayerState.current_song)
    vc.play(discord.FFmpegPCMAudio(full_path), after=play_next)


@tree.command(name="loop", description="🔁 Loop the current song")
async def loop(interaction: discord.Interaction):
    PlayerState.is_looping = not PlayerState.is_looping
    msg = "🔁 Looping the current track." if PlayerState.is_looping else "❌ Stopped looping the track."
    await interaction.response.send_message(msg)


@tree.command(name="stop", description="Stop playback and clear playlist")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("❌ Nothing is playing.")
        return

    vc.stop()
    PlayerState.current_playlist.clear()
    PlayerState.current_folder = None
    PlayerState.current_song = None
    await interaction.response.send_message("🛑 Playback stopped.")


@client.event
async def on_ready():
    await tree.sync()
    print(f"🤖 Logged in as {client.user} and synced commands.")


client.run(TOKEN)
