from flask import Blueprint, jsonify


# Routes for login and registration.
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    # Placeholder route for testing the backend setup.
    return jsonify({
        "success": True,
        "message": "Login route is working"
    })


@auth_bp.route("/register", methods=["POST"])
def register():
    # Placeholder route for testing the backend setup.
    return jsonify({
        "success": True,
        "message": "Register route is working"
    })
