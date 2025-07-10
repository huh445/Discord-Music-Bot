# Discord Music Bot

A Discord bot built using Python and `discord.py` that streams music from YouTube, plays local MP3 files, and supports playlists. Commands are implemented as modern Discord slash commands using `discord.app_commands`.

---

## Features

- Play songs from YouTube URLs or search queries using `yt-dlp`  
- Play local MP3 files stored in a `/songs` folder  
- Play MP3 playlists stored as folders under `/playlist` with auto-queueing  
- Loop the current track toggle  
- Skip, stop, join, and leave voice channel commands  
- Now playing status with current track title  
- Robust voice connection handling and error reporting  

---

## Requirements

- Python 3.10+  
- `discord.py` (latest version with app_commands support)  
- `yt-dlp` for YouTube audio extraction  
- FFmpeg installed and available in your system PATH  
- A Discord bot token with **applications.commands** scope enabled  

---

## Setup & Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/huh445/discordbot1.git
   cd discordbot1
   ```

2. Install dependencies  
   ```bash
   pip install -r requirements.txt
   # requirements.txt should include: discord.py yt-dlp
   ```

3. Make sure FFmpeg is installed and accessible in your terminal/command prompt. Test with `ffmpeg -version`.

4. Create a `.env` file in the root directory and add your Discord bot token:  
   ```env
   DISCORD_TOKEN=your-bot-token-here
   ```

5. Prepare local music folders if you want to use local playback:  
   - Place MP3 files in `/songs` for single file playback  
   - Organize playlists as subfolders under `/playlist` containing MP3s  

6. Run the bot  
   ```bash
   python bot.py
   ```

---

## Usage

The bot uses slash commands. Examples:

| Command         | Description                          | Usage Example                      |
|-----------------|------------------------------------|----------------------------------|
| `/join`         | Join the voice channel you’re in   | `/join`                          |
| `/leave`        | Leave the current voice channel     | `/leave`                         |
| `/play`         | Search and play a song from YouTube| `/play Never Gonna Give You Up`  |
| `/play_url`     | Play a direct YouTube URL           | `/play_url https://youtu.be/...` |
| `/play_mp3`     | Play a local MP3 file from `/songs`| `/play_mp3 mysong.mp3`            |
| `/play_playlist`| Play a folder of MP3s as playlist   | `/play_playlist chillbeats`      |
| `/skip`         | Skip current track                  | `/skip`                         |
| `/nowplaying`   | Show current playing song          | `/nowplaying`                   |
| `/loop`         | Toggle looping of current song     | `/loop`                         |
| `/stop`         | Stop playback and clear queue      | `/stop`                         |

---

## Notes & Recommendations

- Make sure users invoking play commands are connected to a voice channel, or the bot will prompt them to join one first.  
- FFmpeg is critical; ensure your system has it installed and updated for smooth playback.  
- Local MP3 files and playlists need to be correctly placed with matching filenames and extensions.  
- The bot uses `yt-dlp` for robust YouTube extraction; updating it regularly avoids issues with YouTube changes.  
- The bot manages voice connections intelligently, reconnecting and cleaning up after playlists end.

---

## Contributing

Contributions are welcome! Please keep code clean and comment where necessary. Feel free to submit pull requests for feature additions or bug fixes.

---

## License

MIT License — see LICENSE file.
