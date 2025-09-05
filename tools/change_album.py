import eyed3
import os

folder_path = input("Enter folder path: ")
new_album_name = input("Enter new album name: ")
new_artist_name = "huh445"

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".mp3"):
        file_path = os.path.join(folder_path, filename)
        audiofile = eyed3.load(file_path)

        if audiofile is None:
            print(f"Could not load file: {filename}")
            continue

        if audiofile.tag is None:
            audiofile.initTag()

        changed = False

        # Update album
        if audiofile.tag.album != new_album_name:
            audiofile.tag.album = new_album_name
            changed = True

        # Update artist
        if audiofile.tag.artist != new_artist_name:
            audiofile.tag.artist = new_artist_name
            changed = True

        if changed:
            audiofile.tag.save()
            print(f"Updated tags: {filename}")
        else:
            print(f"Skipped (already correct): {filename}")
