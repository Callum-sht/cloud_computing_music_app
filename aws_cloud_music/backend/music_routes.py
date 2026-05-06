import boto3
from boto3.dynamodb.conditions import Key
from flask import Blueprint, jsonify, request


# Routes for music search and query features.
music_bp = Blueprint("music", __name__, url_prefix="/music")


def text_contains(item_value, search_value):
    return search_value.lower() in str(item_value).lower()


def read_all_pages(table, use_query, **kwargs):
    items = []

    if use_query:
        response = table.query(**kwargs)
    else:
        response = table.scan(**kwargs)

    items.extend(response.get("Items", []))

    # Continue reading if DynamoDB returns paginated data.
    while "LastEvaluatedKey" in response:
        kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        if use_query:
            response = table.query(**kwargs)
        else:
            response = table.scan(**kwargs)

        items.extend(response.get("Items", []))

    return items


def item_matches(item, title, year, artist, album):
    title_matches = not title or text_contains(item.get("title", ""), title)
    year_matches = not year or year == str(item.get("year", "")).strip()
    artist_matches = not artist or text_contains(item.get("artist", ""), artist)
    album_matches = not album or text_contains(item.get("album", ""), album)

    return title_matches and year_matches and artist_matches and album_matches


def format_music_item(item):
    return {
        "song_id": item.get("song_id", ""),
        "title": item.get("title", ""),
        "artist": item.get("artist", ""),
        "album": item.get("album", ""),
        "year": item.get("year", ""),
        "s3_img_url": item.get("s3_img_url", "")
    }


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

        if artist and year:
            items = read_all_pages(
                table,
                True,
                IndexName="artist-year-index",
                KeyConditionExpression=Key("artist").eq(artist) & Key("year").eq(year)
            )
        elif album:
            items = read_all_pages(
                table,
                True,
                IndexName="album-artist-index",
                KeyConditionExpression=Key("album").eq(album)
            )
        elif artist:
            items = read_all_pages(
                table,
                True,
                KeyConditionExpression=Key("artist").eq(artist)
            )
        else:
            items = read_all_pages(table, False)

        matched_items = [
            format_music_item(item)
            for item in items
            if item_matches(item, title, year, artist, album)
        ]

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
