import boto3
from flask import Blueprint, jsonify, request


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
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Please fill in all fields"
        }), 400

    email = str(data.get("email", "")).strip()
    user_name = str(data.get("user_name", "")).strip()
    password = str(data.get("password", "")).strip()

    if not email or not user_name or not password:
        return jsonify({
            "success": False,
            "message": "Please fill in all fields"
        }), 400

    try:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.Table("login")

        # Check if the email is already registered.
        existing_user = table.get_item(Key={"email": email})
        if "Item" in existing_user:
            return jsonify({
                "success": False,
                "message": "The email already exists"
            }), 409

        # Save the new user in DynamoDB.
        table.put_item(Item={
            "email": email,
            "user_name": user_name,
            "password": password
        })

        return jsonify({
            "success": True,
            "message": "Registered successfully"
        })

    except Exception:
        return jsonify({
            "success": False,
            "message": "Registration failed"
        }), 500
