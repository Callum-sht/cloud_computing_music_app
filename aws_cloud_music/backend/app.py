from flask import Flask, jsonify
from flask_cors import CORS

from auth_routes import auth_bp
from music_routes import music_bp
from subscription_routes import subscription_bp


# Create the Flask application.
app = Flask(__name__)

# Enable CORS for requests from the frontend.
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(music_bp)
app.register_blueprint(subscription_bp)


@app.route("/health", methods=["GET"])
def health_check():
    # Simple endpoint to check that the backend is running.
    return jsonify({
        "success": True,
        "message": "EC2 backend is running"
    })


if __name__ == "__main__":
    # Run the Flask app on the EC2 instance.
    app.run(host="0.0.0.0", port=80)
