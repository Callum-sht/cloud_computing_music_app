import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request


# Routes for user subscriptions.
subscription_bp = Blueprint("subscription", __name__, url_prefix="/subscription")

REGION = "us-east-1"
SUBSCRIPTION_TABLE = "subscription"
MUSIC_TABLE = "music"


def get_dynamodb():
    return boto3.resource("dynamodb", region_name=REGION)


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


def find_song_by_id(music_table, song_id):
    items = read_all_pages(music_table, False)

    for item in items:
        if item.get("song_id") == song_id:
            return item

    return None


def format_subscription_item(item):
    return {
        "song_id": item.get("song_id", ""),
        "title": item.get("title", ""),
        "artist": item.get("artist", ""),
        "album": item.get("album", ""),
        "year": item.get("year", ""),
        "s3_img_url": item.get("s3_img_url", "")
    }


@subscription_bp.route("/list", methods=["POST"])
def list_subscriptions():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "user_email is required"
        }), 400

    user_email = str(data.get("user_email", "")).strip()

    if not user_email:
        return jsonify({
            "success": False,
            "message": "user_email is required"
        }), 400

    try:
        dynamodb = get_dynamodb()
        table = dynamodb.Table(SUBSCRIPTION_TABLE)

        items = read_all_pages(
            table,
            True,
            KeyConditionExpression=Key("user_email").eq(user_email)
        )

        return jsonify({
            "success": True,
            "items": [format_subscription_item(item) for item in items]
        })

    except Exception as error:
        print("Subscription list error:", error)
        return jsonify({
            "success": False,
            "message": "Failed to load subscriptions"
        }), 500


@subscription_bp.route("/add", methods=["POST"])
def add_subscription():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "user_email and song_id are required"
        }), 400

    user_email = str(data.get("user_email", "")).strip()
    song_id = str(data.get("song_id", "")).strip()

    if not user_email or not song_id:
        return jsonify({
            "success": False,
            "message": "user_email and song_id are required"
        }), 400

    try:
        dynamodb = get_dynamodb()
        subscription_table = dynamodb.Table(SUBSCRIPTION_TABLE)
        music_table = dynamodb.Table(MUSIC_TABLE)

        existing_subscription = subscription_table.get_item(
            Key={
                "user_email": user_email,
                "song_id": song_id
            }
        )

        if "Item" in existing_subscription:
            return jsonify({
                "success": False,
                "message": "This song is already subscribed"
            })

        song = find_song_by_id(music_table, song_id)

        if not song:
            return jsonify({
                "success": False,
                "message": "Song not found"
            })

        subscription_table.put_item(Item={
            "user_email": user_email,
            "song_id": song_id,
            "artist": song.get("artist", ""),
            "title": song.get("title", ""),
            "album": song.get("album", ""),
            "year": song.get("year", ""),
            "s3_img_url": song.get("s3_img_url", ""),
            "subscribed_at": datetime.now(timezone.utc).isoformat()
        })

        return jsonify({
            "success": True,
            "message": "Subscribed successfully"
        })

    except Exception as error:
        print("Subscription add error:", error)
        return jsonify({
            "success": False,
            "message": "Subscription failed"
        }), 500


@subscription_bp.route("/remove", methods=["POST"])
def remove_subscription():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "user_email and song_id are required"
        }), 400

    user_email = str(data.get("user_email", "")).strip()
    song_id = str(data.get("song_id", "")).strip()

    if not user_email or not song_id:
        return jsonify({
            "success": False,
            "message": "user_email and song_id are required"
        }), 400

    try:
        dynamodb = get_dynamodb()
        table = dynamodb.Table(SUBSCRIPTION_TABLE)

        table.delete_item(Key={
            "user_email": user_email,
            "song_id": song_id
        })

        return jsonify({
            "success": True,
            "message": "Removed successfully"
        })

    except Exception as error:
        print("Subscription remove error:", error)
        return jsonify({
            "success": False,
            "message": "Subscription failed"
        }), 500
