import boto3
from flask import Blueprint, jsonify, request


# Routes for music search and query features.
music_bp = Blueprint("music", __name__, url_prefix="/music")


@music_bp.route("/query", methods=["POST"])
def query_music():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Please fill in at least one field"
        }), 400

    title = str(data.get("title", "")).strip()
    year = str(data.get("year", "")).strip()
    artist = str(data.get("artist", "")).strip()
    album = str(data.get("album", "")).strip()

    if not title and not year and not artist and not album:
        return jsonify({
            "success": False,
            "message": "Please fill in at least one field"
        }), 400

    try:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.Table("music")

        all_items = []
        response = table.scan()
        all_items.extend(response.get("Items", []))

        # Continue scanning if DynamoDB returns paginated data.
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            all_items.extend(response.get("Items", []))

        matched_items = []

        for item in all_items:
            item_title = str(item.get("title", ""))
            item_year = str(item.get("year", "")).strip()
            item_artist = str(item.get("artist", ""))
            item_album = str(item.get("album", ""))

            title_matches = not title or title.lower() in item_title.lower()
            year_matches = not year or year == item_year
            artist_matches = not artist or artist.lower() in item_artist.lower()
            album_matches = not album or album.lower() in item_album.lower()

            if title_matches and year_matches and artist_matches and album_matches:
                matched_items.append({
                    "song_id": item.get("song_id", ""),
                    "title": item.get("title", ""),
                    "artist": item.get("artist", ""),
                    "album": item.get("album", ""),
                    "year": item.get("year", ""),
                    "s3_img_url": item.get("s3_img_url", "")
                })

        if not matched_items:
            return jsonify({
                "success": False,
                "message": "No result is retrieved. Please query again"
            })

        return jsonify({
            "success": True,
            "items": matched_items
        })

    except Exception as error:
        print("Music query error:", error)
        return jsonify({
            "success": False,
            "message": "Query failed"
        }), 500
