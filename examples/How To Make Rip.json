# Guide: Extracting Metadata from FLAC CD Rips

This guide will show you how to extract metadata from FLAC files, such as the album name, artist, and track details, and generate a JSON playlist that you can use for your own purposes.

## Prerequisites

Before you run the script, you need to install the `mutagen` library to handle FLAC files.

### Install Mutagen

Run the following command to install the necessary library:

   ```
    pip install mutagen
   ```

**Instructions**
1. Prepare Your FLAC Files

    •Place the FLAC files from your CD rip into a folder. These files will be processed by the script.

2. Create the Python Script

    •Inside the folder containing your FLAC files, create a new Python file (e.g., generate_playlist.py).

3. Edit the Python Script

    •Copy and paste the following code into your Python file.

    •Modify the variables in the script to reflect the correct album name, artist name, and any other necessary   details.

```
import os
import json
from mutagen.flac import FLAC

folder_path = os.getcwd()

album_name  = "ALBUM NAME"
artist_name = "ARTIST NAME"
playlist_description = f"Playlist created from local folder: {album_name}"

def generate_playlist_json(folder_path, album_name, artist_name, playlist_description):
    flac_files = [f for f in os.listdir(folder_path) if f.endswith('.flac')]

    tracks = []
    for idx, file in enumerate(flac_files, 1):
        file_path = os.path.join(folder_path, file)
        audio_file = FLAC(file_path)

        track_name = audio_file.get('title', [file])[0]
        artist_name = audio_file.get('artist', ["Unknown Artist"])[0]
        album_name = audio_file.get('album', ["Unknown Album"])[0]
        release_date = audio_file.get('date', ["Unknown Year"])[0]
        duration_ms = int(audio_file.info.length * 1000)

        track_info = {
            "track": {
                "name": track_name,
                "artists": [{"name": artist_name}],
                "album": {
                    "name": album_name,
                    "release_date": release_date
                },
                "duration_ms": duration_ms,
                "uri": f"local:{track_name}",
                "is_local": True,
                "track_number": idx,
                "disc_number": 1,
                "external_urls": {},
                "type": "track"
            }
        }
        tracks.append(track_info)

    playlist_data = {
        "name": album_name,
        "description": playlist_description,
        "owner": {
            "display_name": artist_name
        },
        "tracks": {
            "total": len(flac_files),
            "items": tracks
        },
        "public": False,
        "collaborative": False,
        "followers": {
            "total": 0
        },
        "id": None,
        "uri": f"local:playlist:{album_name}",
        "external_urls": {},
        "href": None,
        "images": [],
        "type": "playlist"
    }

    output_file = os.path.join(folder_path, "playlist.json")
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(playlist_data, json_file, ensure_ascii=False, indent=4)

    print(f"Playlist JSON file has been created at: {output_file}")

generate_playlist_json(folder_path, album_name, artist_name, playlist_description)

```


### 4. Run the Script

-   After editing the variables, save the Python file.
    
-   Run the Python script using the following command:

   ```
    python generate_playlist.py
 ```

The script will scan the folder for FLAC files, extract the metadata from each file, and generate a `playlist.json` file with all the track information. The `playlist.json` file will be saved in the same directory as the FLAC files.






