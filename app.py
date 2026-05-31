from flask import Flask, request, jsonify
import requests
from urllib.parse import quote
import re

app = Flask(__name__)

# ============================
#   NOXEN API - CREDIT CONFIG
# ============================
CREDIT = {
    "api_name": "NoxenAPI",
    "version": "v1.0",
    "developers": ["@B4DAL", "@NoxenOwner"],
    "channels": [
        {"name": "BadalPvt", "link": "https://t.me/BadalPvt"},
        {"name": "NoxenCode", "link": "https://t.me/NoxenCode"},
        {"name": "NoxenBots", "link": "https://t.me/NoxenBots"},
    ],
    "note": "Powered by NoxenAPI | Join our channels for more bots & tools!",
}

INSTA_REGEX = re.compile(
    r'(?:https?://)?(?:www\.)?instagram\.com/(p|reel|tv)/([a-zA-Z0-9\-_]+)'
)

# ============================
#        HOME ROUTE
# ============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Welcome to NoxenAPI!",
        "credit": CREDIT,
        "endpoints": {
            "download": "/down?url=<instagram_url>",
            "ping": "/ping",
        }
    })

# ============================
#        PING ROUTE
# ============================
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "success": True,
        "message": "Pong! 🏓 NoxenAPI is alive!",
        "credit": CREDIT,
    })

# ============================
#      DOWNLOAD ROUTE
# ============================
@app.route("/down", methods=["GET"])
def download():
    url = request.args.get("url", "").strip()

    # Validate URL provided
    if not url:
        return jsonify({
            "success": False,
            "message": "❌ Please provide a URL. Example: /down?url=https://instagram.com/reel/xxx",
            "credit": CREDIT,
        }), 400

    # Validate Instagram URL
    if not INSTA_REGEX.search(url):
        return jsonify({
            "success": False,
            "message": "❌ Invalid Instagram URL! Send a valid post/reel link.",
            "credit": CREDIT,
        }), 400

    try:
        # Call original tele-social API
        api_url = f"https://tele-social.vercel.app/down?url={quote(url)}"
        response = requests.get(api_url, timeout=25)
        response.raise_for_status()
        data = response.json()

        # Check if original API returned success
        if data.get("status") == True and "data" in data:
            media_data = data["data"].get("media", {})
            return jsonify({
                "success": True,
                "message": "✅ Media fetched successfully!",
                "data": {
                    "type": data["data"].get("type", "unknown"),
                    "media": {
                        "video": media_data.get("video"),
                        "image": media_data.get("image"),
                    },
                    "original_url": url,
                },
                "credit": CREDIT,
            })
        else:
            return jsonify({
                "success": False,
                "message": data.get("message", "❌ Could not fetch media. Post might be private."),
                "credit": CREDIT,
            }), 422

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "message": "❌ Request timed out! Try again.",
            "credit": CREDIT,
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "message": f"❌ API Error: {str(e)}",
            "credit": CREDIT,
        }), 500

# ============================
#       404 HANDLER
# ============================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "message": "❌ Route not found!",
        "credit": CREDIT,
    }), 404

# ============================
#         RUN APP
# ============================
if __name__ == "__main__":
    app.run(debug=True, port=8000)
