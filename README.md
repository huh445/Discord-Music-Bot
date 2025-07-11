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
- Eyed3 for tools
- DotEnv for getting the environment variable for running the bot

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
   ```

3. Make sure FFmpeg is installed and accessible in your terminal/command prompt. Test with `ffmpeg -version`.

4. Add your DISCORD_TOKEN to your Environment Variables.

5. Prepare local music folders if you want to use local playback:  
   - Place MP3 files in `/songs` for single file playback  
   - Organize playlists as subfolders under `/playlist` containing MP3s  

6. Run the bot  
   ```bash
   python main.py
   ```

---

## Usage

The bot uses slash commands. Examples:

| Command         | Description                        | Usage Example                    |
|-----------------|------------------------------------|----------------------------------|
| `/join`         | Join the voice channel you’re in   | `/join`                          |
| `/leave`        | Leave the current voice channel    | `/leave`                         |
| `/play`         | Search and play a song from YouTube| `/play Never Gonna Give You Up`  |
| `/play_url`     | Play a direct mp3 or youtube URL   | `/play_url https://youtu.be/...` |
| `/play_mp3`     | Play a local MP3 file from `/songs`| `/play_mp3 mysong.mp3`           |
| `/play_playlist`| Play a folder of MP3s as playlist  | `/play_playlist chillbeats`      |
| `/skip`         | Skip current track                 | `/skip`                          |
| `/nowplaying`   | Show current playing song          | `/nowplaying`                    |
| `/loop`         | Toggle looping of current song     | `/loop`                          |
| `/stop`         | Stop playback and clear queue      | `/stop`                          |

---

## Contributing

Contributions are welcome! Please keep code clean and comment where necessary. Feel free to submit pull requests for feature additions or bug fixes.

---

## Known Bugs

- Playlist errors with /stop and /loop commands
- /stop command not working properly
- /loop command having unintended issues with FFmpeg

---

## License

MIT License — see LICENSE file.
