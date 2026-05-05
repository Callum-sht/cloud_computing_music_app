import json
import re
import sys
from pathlib import Path
from urllib.parse import quote
import boto3

REGION = "us-east-1"
BUCKET_NAME = "group48-cloud-music-assets-s4060865"
TABLE_NAME = "music"
JSON_FILE = "2026a2_songs.json"

def load_songs_from_json(json_file):
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

def s3_image_url(artist):
    """Create the S3 image URL directly from the artist name."""
    key = quote(artist_image_key(artist), safe="/")
    return f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{key}"

def make_song_id(song):
    """Create a stable ID directly from song fields."""
    artist = str(song.get("artist", "")).strip()
    album = str(song.get("album", "")).strip()
    title = str(song.get("title", "")).strip()
    year = str(song.get("year", "")).strip()

    return f"{artist}|{album}|{title}|{year}"

def main():
    json_file = sys.argv[1] if len(sys.argv) > 1 else JSON_FILE
    songs = load_songs_from_json(json_file)
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    success_count = 0
    failure_count = 0

    with table.batch_writer() as batch:
        for song in songs:
            try:
                artist = str(song.get("artist", "")).strip()
                album = str(song.get("album", "")).strip()
                title = str(song.get("title", "")).strip()
                year = str(song.get("year", "")).strip()

                if not artist or not album or not title:
                    raise ValueError("artist, album, or title is missing")
                
                item = {
                    "song_id": make_song_id(song),
                    "title": title,
                    "artist": artist,
                    "album": album,
                    "year": year,
                    "s3_img_url": s3_image_url(artist),
                    "album_title": f"{album}#{title}",
                    "artist_title": f"{artist}#{title}",
                }
                
                # keep the original image URL for reference/debugging.

                if song.get("img_url"):
                    item["img_url"] = str(song["img_url"]).strip()
                    
                batch.put_item(Item=item)

                success_count += 1
                print(f"Loaded {artist} - {title}")

            except Exception as error:
                failure_count += 1
                print(f"Skipped one song because of error: {error}")

    print(f"Done. Loaded {success_count} songs. Failed: {failure_count}.")

if __name__ == "__main__":
    main()
