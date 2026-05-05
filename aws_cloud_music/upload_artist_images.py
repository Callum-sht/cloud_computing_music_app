import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import boto3


REGION = "us-east-1"
BUCKET_NAME = "group48-cloud-music-assets-s4060865"
JSON_FILE = "2026a2_songs.json"


def load_songs_from_json(json_file):
    """Read songs from the JSON file."""
    path = Path(json_file)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict) and "songs" in data:
        return data["songs"]

    return data


def format_artist_name(artist):
    """Change artist name into a simple file-friendly format."""
    artist = str(artist).strip().lower()
    artist = artist.replace("&", "and")
    artist = re.sub(r"[^a-z0-9]+", "-", artist)
    artist = re.sub(r"-+", "-", artist).strip("-")
    return artist


def artist_image_key(artist):
    return f"images/artists/{format_artist_name(artist)}.jpg"


def download_image(img_url):
    """Download image bytes from the img_url field."""
    request = Request(img_url, headers={"User-Agent": "cloud-music-app/1.0"})

    with urlopen(request, timeout=20) as response:
        image_data = response.read()

    return image_data


def main():
    json_file = sys.argv[1] if len(sys.argv) > 1 else JSON_FILE

    try:
        songs = load_songs_from_json(json_file)
    except FileNotFoundError:
        print(f"Error: could not find JSON file: {json_file}")
        return
    except json.JSONDecodeError as error:
        print(f"Error: JSON file is not valid: {error}")
        return

    if not isinstance(songs, list):
        print("Error: JSON data must be a list of songs or contain a 'songs' list.")
        return

    s3 = boto3.client("s3", region_name=REGION)

    uploaded_artists = set()
    uploaded_count = 0
    skipped_count = 0
    failed_count = 0

    for song in songs:
        artist = str(song.get("artist", "")).strip()
        img_url = str(song.get("img_url", "")).strip()

        if not artist or not img_url:
            skipped_count += 1
            print("Skipped one record because artist or img_url is missing.")
            continue

        if artist in uploaded_artists:
            skipped_count += 1
            continue

        key = artist_image_key(artist)

        try:
            image_data = download_image(img_url)

            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=image_data,
                ContentType="image/jpeg",
            )

            uploaded_artists.add(artist)
            uploaded_count += 1
            print(f"Uploaded {artist} -> s3://{BUCKET_NAME}/{key}")

        except (HTTPError, URLError, TimeoutError) as error:
            failed_count += 1
            print(f"Failed to download image for {artist}: {error}")

        except Exception as error:
            failed_count += 1
            print(f"Failed to upload image for {artist}: {error}")

    print("Upload summary:")
    print(f"Unique artist images uploaded: {uploaded_count}")
    print(f"Skipped records: {skipped_count}")
    print(f"Failed uploads: {failed_count}")


if __name__ == "__main__":
    main()