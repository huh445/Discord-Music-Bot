# player.py
class PlayerState:
    def __init__(self):
        self.current_playlist = []
        self.current_folder = None
        self.current_song = None
        self.is_looping = False
        self.current_source = None   # Hold FFmpegPCMAudio object
