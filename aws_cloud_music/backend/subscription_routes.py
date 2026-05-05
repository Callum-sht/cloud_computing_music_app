from flask import Blueprint, jsonify


# Routes for user subscriptions.
subscription_bp = Blueprint("subscription", __name__, url_prefix="/subscription")


@subscription_bp.route("/list", methods=["GET"])
def list_subscriptions():
    # Placeholder route for testing the backend setup.
    return jsonify({
        "success": True,
        "message": "Subscription list route is working"
    })


@subscription_bp.route("/add", methods=["POST"])
def add_subscription():
    # Placeholder route for testing the backend setup.
    return jsonify({
        "success": True,
        "message": "Subscription add route is working"
    })


@subscription_bp.route("/remove", methods=["POST"])
def remove_subscription():
    # Placeholder route for testing the backend setup.
    return jsonify({
        "success": True,
        "message": "Subscription remove route is working"
    })
