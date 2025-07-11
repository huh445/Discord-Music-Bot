# cogs/music.py
import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp

from player import PlayerState
from utils import is_url, ensure_voice, get_loop_after

# Shared FFmpeg and yt-dlp options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'source_address': '0.0.0.0',
    'user_agent': 'Mozilla/5.0'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.player_state = PlayerState()

    # /join
    @app_commands.command(name="join", description="Join your voice channel")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
            await interaction.response.send_message("✅ Joined your channel.")
        else:
            await interaction.response.send_message("❌ Please join a voice channel first.")

    # /leave
    @app_commands.command(name="leave", description="Leave the voice channel")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("👋 Disconnected.")
        else:
            await interaction.response.send_message("❌ I'm not connected.")

    # /play
    @app_commands.command(name="play", description="Search and play from YouTube")
    @app_commands.describe(search="Song name or URL")
    async def play(self, interaction: discord.Interaction, search: str):
        vc = await ensure_voice(interaction)
        if not vc:
            return

        await interaction.response.send_message(f"🔍 Searching `{search}`…")
        try:
            query = search if is_url(search) else f"ytsearch:{search}"
            info = ytdl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]

            url = info['url']
            title = info.get('title', 'Unknown')
            self.player_state.current_song = title

            # build a factory for fresh FFmpegPCMAudio sources
            source_factory = lambda: discord.FFmpegPCMAudio(url, **ffmpeg_options)
            source = source_factory()
            self.player_state.current_source = source

            vc.play(source, after=get_loop_after(vc, self.player_state, source_factory))
            await interaction.followup.send(f"▶️ Now playing **{title}**")

        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {e}")


    # /play_url
    @app_commands.command(name="play_url", description="Play a YouTube audio stream from a URL")
    @app_commands.describe(url="Direct YouTube URL")
    async def play_url(self, interaction: discord.Interaction, url: str):
        vc = await ensure_voice(interaction)
        if not vc:
            return

        await interaction.response.send_message("🔗 Loading URL…")
        try:
            data = ytdl.extract_info(url, download=False)
            if 'entries' in data:
                data = data['entries'][0]

            stream_url = data['url']
            title = data.get('title', 'Unknown')
            self.player_state.current_song = title

            source_factory = lambda: discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
            source = source_factory()
            self.player_state.current_source = source

            vc.stop()
            vc.play(source, after=get_loop_after(vc, self.player_state, source_factory))
            await interaction.followup.send(f"🎧 Streaming URL: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {e}")

    # /play_mp3
    @app_commands.command(name="play_mp3", description="Play a local MP3 from /songs")
    @app_commands.describe(filename="Name of the file in /songs")
    async def play_mp3(self, interaction: discord.Interaction, filename: str):
        vc = await ensure_voice(interaction)
        if not vc:
            return

        path = os.path.join("songs", filename)
        if not os.path.isfile(path):
            await interaction.response.send_message(f"❌ File `{filename}` not found.")
            return

        self.player_state.current_song = filename
        source_factory = lambda: discord.FFmpegPCMAudio(path)
        source = source_factory()
        self.player_state.current_source = source

        vc.stop()
        vc.play(source, after=get_loop_after(vc, self.player_state, source_factory))
        await interaction.response.send_message(f"🎵 Playing local file: **{filename}**")

    # /play_playlist
    @app_commands.command(name="play_playlist", description="Play a folder of MP3s as a playlist")
    @app_commands.describe(playlist_name="Folder name in /playlist")
    async def play_playlist(self, interaction: discord.Interaction, playlist_name: str):
        vc = await ensure_voice(interaction)
        if not vc:
            return

        folder = os.path.join("playlist", playlist_name)
        if not os.path.isdir(folder):
            await interaction.response.send_message(f"❌ Playlist `{playlist_name}` not found.")
            return

        files = sorted(f for f in os.listdir(folder) if f.endswith(".mp3"))
        if not files:
            await interaction.response.send_message("❌ No MP3s in that playlist.")
            return

        # initialize playlist
        self.player_state.current_playlist = files.copy()
        self.player_state.current_folder = folder
        self.player_state.current_song = self.player_state.current_playlist.pop(0)

        first_path = os.path.join(folder, self.player_state.current_song)
        source = discord.FFmpegPCMAudio(first_path)
        self.player_state.current_source = source

        vc.stop()
        vc.play(source, after=lambda err: self._play_next(err, interaction.channel, vc))

        await interaction.response.send_message(
            f"📻 Started playlist **{playlist_name}**: **{self.player_state.current_song}**"
        )

    # play next song in playlist
    def _play_next(self, error, text_channel: discord.abc.Messageable, vc: discord.VoiceClient):
        if error:
            print(f"❗ Playback error: {error}")

        if self.player_state.current_playlist:
            next_song = self.player_state.current_playlist.pop(0)
            self.player_state.current_song = next_song
            path = os.path.join(self.player_state.current_folder, next_song)

            source = discord.FFmpegPCMAudio(path)
            self.player_state.current_source = source

            coro = text_channel.send(f"▶️ Now playing: **{next_song}**")
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

            vc.play(source, after=lambda err: self._play_next(err, text_channel, vc))
        else:
            coro = text_channel.send("✅ Playlist finished.")
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

            if self.player_state.current_source:
                self.player_state.current_source.cleanup()
                self.player_state.current_source = None

            self.player_state.current_song = None
            self.player_state.current_folder = None
            self.player_state.current_playlist.clear()

    # /skip
    @app_commands.command(name="skip", description="Skip current song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            if self.player_state.current_source:
                self.player_state.current_source.cleanup()
            await interaction.response.send_message(f"⏭️ Skipped **{self.player_state.current_song}**")
        else:
            await interaction.response.send_message("❌ Nothing playing.")

    # /now_playing
    @app_commands.command(name="now_playing", description="Show current song")
    async def nowplaying(self, interaction: discord.Interaction):
        song = self.player_state.current_song
        await interaction.response.send_message(
            f"🎧 Now playing **{song}**" if song else "❌ No song playing."
        )

    # /loop
    @app_commands.command(name="loop", description="Toggle looping of current song")
    async def loop(self, interaction: discord.Interaction):
        self.player_state.is_looping = not self.player_state.is_looping
        msg = "🔁 Looping enabled." if self.player_state.is_looping else "🔁 Looping disabled."
        await interaction.response.send_message(msg)

    # /stop
    @app_commands.command(name="stop", description="Stop playback and clear queue")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            await interaction.response.send_message("❌ Nothing to stop.")
            return

        vc.stop()
        if self.player_state.current_source:
            self.player_state.current_source.cleanup()
            self.player_state.current_source = None

        self.player_state.current_playlist.clear()
        self.player_state.current_folder = None
        self.player_state.current_song = None

        await interaction.response.send_message("🛑 Playback stopped and cleared.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
