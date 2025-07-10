import eyed3
import os

folder_path = input("Enter folder path: ")
new_album_name = input("Enter new name: ")

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".mp3"):
        file_path = os.path.join(folder_path, filename)
        audiofile = eyed3.load(file_path)
        if audiofile and audiofile.tag.album != new_album_name:
            audiofile.tag.album = new_album_name
            audiofile.tag.save()
            print(f"Updated album tag: {filename}")
        else:
            print(f"Skipped (same name): {filename}")
