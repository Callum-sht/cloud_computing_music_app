from flask import Blueprint, jsonify


# Routes for music search and query features.
music_bp = Blueprint("music", __name__, url_prefix="/music")


@music_bp.route("/query", methods=["POST"])
def query_music():
    # Placeholder route for testing the backend setup.
    return jsonify({
        "success": True,
        "message": "Music query route is working"
    })
