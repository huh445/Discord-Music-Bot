import eyed3

def copy_metadata(src_file, dest_file):
    src_audio = eyed3.load(src_file)
    dest_audio = eyed3.load(dest_file)

    if not src_audio.tag or not dest_audio.tag:
        print("One of the files has no tag — initializing...")
        if not src_audio.tag:
            src_audio.initTag()
        if not dest_audio.tag:
            dest_audio.initTag()

    dest_audio.tag.title = src_audio.tag.title
    dest_audio.tag.artist = src_audio.tag.artist
    dest_audio.tag.album = src_audio.tag.album
    dest_audio.tag.album_artist = src_audio.tag.album_artist
    dest_audio.tag.genre = src_audio.tag.genre
    track = src_audio.tag.track_num
    dest_audio.tag.track_num = (track[0], track[1]) if track else None

    dest_audio.tag.release_date = src_audio.tag.release_date
    dest_audio.tag.recording_date = src_audio.tag.recording_date
    dest_audio.tag.comments.set(src_audio.tag.comments[0].text if src_audio.tag.comments else '')

    dest_audio.tag.save()
    print(f"Metadata copied from '{src_file}' to '{dest_file}'")


copy_metadata(input("Song 1: "), input("Song 2: "))