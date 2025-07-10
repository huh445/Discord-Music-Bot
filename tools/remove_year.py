import os
import eyed3

# Your target folder
folder_path = input("Input your folder path: ")
year_change = int(input("Input the year you want to change to: "))

for filename in os.listdir(folder_path):
    if not filename.lower().endswith(".mp3"):
        continue

    filepath = os.path.join(folder_path, filename)
    audio = eyed3.load(filepath)

    if audio is None or audio.tag is None:
        print(f"Skipping (no tag): {filename}")
        continue

    tags_removed = False

    # Remove year/date-related fields
    if audio.tag.recording_date != eyed3.core.Date(year=year_change):
        audio.tag.recording_date = eyed3.core.Date(year=year_change)
        tags_removed = True
    if audio.tag.release_date != eyed3.core.Date(year=year_change):
        audio.tag.release_date = eyed3.core.Date(year=year_change)
        tags_removed = True
    if audio.tag.original_release_date != eyed3.core.Date(year=year_change):
        audio.tag.original_release_date = eyed3.core.Date(year=year_change)
        tags_removed = True

    if tags_removed:
        audio.tag.save()
        print(f"✅ Changed year metadata in {filename}")
    else:
        print(f"ℹ️ Year metadata already {year_change} in {filename}")

print("🎯 Done.")
