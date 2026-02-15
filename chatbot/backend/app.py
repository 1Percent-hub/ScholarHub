import os
import time
from flask import Flask, request, jsonify, send_from_directory

from memory_engine import get_reply_with_memory

app = Flask(__name__)

# Folder containing the chat page (index.html, style.css, script.js)
WIDGET_DIR = os.path.join(os.path.dirname(__file__), "..", "widget")
# School Resource app with AI widget (sibling of chatbot folder)
APP_WITH_AI_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "calculator-with-ai")


def after_request(response):
    """Add CORS headers so the widget on any site can call this API."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


app.after_request(after_request)


@app.route("/")
def index():
    """Serve the chat page so opening http://localhost:5000 shows Josiah."""
    return send_from_directory(WIDGET_DIR, "index.html")


@app.route("/<path:filename>")
def widget_static(filename):
    """Serve style.css and script.js for the chat page."""
    if filename in ("style.css", "script.js"):
        return send_from_directory(WIDGET_DIR, filename)
    return "", 404


@app.route("/app/")
def app_with_ai_index():
    """Serve School Resource with AI at http://localhost:5000/app/"""
    if not os.path.isdir(APP_WITH_AI_DIR):
        return "Calculator-with-AI folder not found.", 404
    return send_from_directory(APP_WITH_AI_DIR, "index.html")


@app.route("/app/<path:filename>")
def app_with_ai_static(filename):
    """Serve static assets for School Resource with AI."""
    if not os.path.isdir(APP_WITH_AI_DIR):
        return "", 404
    return send_from_directory(APP_WITH_AI_DIR, filename)


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    session_id = data.get("session_id") or request.headers.get("X-Session-ID") or "default"
    time.sleep(0.9)  # Short "thinking" delay so the UI can show loading state
    reply, suggested, memory_hint = get_reply_with_memory(user_message, session_id)
    payload = {"reply": reply, "suggested": suggested}
    if memory_hint:
        payload["memory_hint"] = memory_hint
    return jsonify(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
