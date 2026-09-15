import base64
import hashlib
import hmac
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

SECRET = os.environ.get("TOKEN_SECRET", "taskflow-classroom")
DEMO_EMAIL = "student@example.com"
DEMO_PASSWORD = "123456"

profile = {
    "id": "u-1",
    "name": "Aung Ko",
    "email": DEMO_EMAIL,
    "photoUrl": None,
}

PRODUCTS = [
    {"product_id": "p-1", "title": "Notebook Pro", "type": "Stationery", "amount": 4.5},
    {"product_id": "p-2", "title": "Task Stickers", "type": "Stationery", "amount": 2.0},
    {"product_id": "p-3", "title": "Focus Timer", "type": "Gadgets", "amount": 18.0},
    {"product_id": "p-4", "title": "Desk Lamp", "type": "Gadgets", "amount": 32.0},
    {"product_id": "p-5", "title": "Water Bottle", "type": "Lifestyle", "amount": 12.0},
    {"product_id": "p-6", "title": "Canvas Backpack", "type": "Lifestyle", "amount": 45.0},
    {"product_id": "p-7", "title": "Kotlin Handbook", "type": "Books", "amount": 22.0},
    {"product_id": "p-8", "title": "Android Workbook", "type": "Books", "amount": 19.0},
    {"product_id": "p-9", "title": "Wireless Mouse", "type": "Gadgets", "amount": 16.0},
    {"product_id": "p-10", "title": "Plant Pot", "type": "Lifestyle", "amount": 9.0},
]


def issue_token(email: str) -> str:
    payload = base64.urlsafe_b64encode(email.encode()).decode().rstrip("=")
    signature = hmac.new(SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()[:24]
    return f"tf.{payload}.{signature}"


def email_from_auth() -> str | None:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.removeprefix("Bearer ").strip()
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "tf":
        return None
    try:
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        email = base64.urlsafe_b64decode(padded).decode()
    except (ValueError, UnicodeDecodeError):
        return None
    expected = issue_token(email)
    if not hmac.compare_digest(token, expected):
        return None
    return email


def unauthorized():
    return jsonify({"message": "Unauthorized"}), 401


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
    return response


@app.route("/", methods=["GET"])
@app.route("/v1", methods=["GET"])
def index():
    return jsonify(
        {
            "name": "TaskFlow classroom API",
            "base": "/v1",
            "demo": {"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
            "routes": [
                "POST /v1/auth/login",
                "GET /v1/profile/me",
                "PUT /v1/profile/me",
                "POST /v1/profile/me/photo",
                "GET /v1/products?q=&page=",
            ],
        }
    )


@app.route("/v1/<path:_unused>", methods=["OPTIONS"])
def preflight(_unused):
    return ("", 204)


@app.post("/v1/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    email = str(body.get("email", "")).strip()
    password = str(body.get("password", ""))
    if email == DEMO_EMAIL and password == DEMO_PASSWORD:
        return jsonify(
            {
                "token": issue_token(email),
                "user": {"id": "u-1", "name": profile["name"], "email": email},
            }
        )
    return jsonify({"message": "Invalid credentials"}), 401


@app.get("/v1/profile/me")
def get_profile():
    if email_from_auth() is None:
        return unauthorized()
    return jsonify(profile)


@app.put("/v1/profile/me")
def update_profile():
    if email_from_auth() is None:
        return unauthorized()
    body = request.get_json(silent=True) or {}
    for key in ("name", "email", "photoUrl"):
        if key in body:
            profile[key] = body[key]
    return jsonify(profile)


@app.post("/v1/profile/me/photo")
def upload_photo():
    if email_from_auth() is None:
        return unauthorized()
    if "photo" not in request.files and "photo" not in request.form:
        return jsonify({"message": "Missing photo part"}), 400
    profile["photoUrl"] = "https://taskflow.local/mock/photo.jpg"
    return jsonify(profile)


@app.get("/v1/products")
def products():
    query = request.args.get("q", "").strip().lower()
    if query == "error":
        return jsonify({"message": "Search service unavailable"}), 500
    page = max(int(request.args.get("page", 1) or 1), 1)
    filtered = [
        item
        for item in PRODUCTS
        if query in item["title"].lower() or query in item["type"].lower()
    ] if query else PRODUCTS
    size = 10
    start = (page - 1) * size
    return jsonify(filtered[start : start + size])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
