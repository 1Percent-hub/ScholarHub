import json
import os
import time
import uuid
from collections import deque
from flask import Flask, request, jsonify, send_from_directory

from memory_engine import get_reply_with_memory

app = Flask(__name__)

# --- Global chat (in-memory; resets on deploy) ---
GLOBAL_CHAT_MAX_MESSAGES = 500
GLOBAL_CHAT_RATE_LIMIT_SECONDS = 2
GLOBAL_CHAT_MESSAGES = deque(maxlen=GLOBAL_CHAT_MAX_MESSAGES)
_global_chat_last_send = {}  # key (userId or ip) -> timestamp

# Folder containing the chat page (index.html, style.css, script.js)
WIDGET_DIR = os.path.join(os.path.dirname(__file__), "..", "widget")
# Academic Arsenal app with AI widget (sibling of chatbot folder)
APP_WITH_AI_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "calculator-with-ai")
MUSIC_DIR = os.path.join(APP_WITH_AI_DIR, "music")
ALLOWED_MUSIC_EXT = (".mp3", ".ogg", ".m4a", ".wav")


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
    """Serve Academic Arsenal with AI at http://localhost:5000/app/"""
    if not os.path.isdir(APP_WITH_AI_DIR):
        return "Calculator-with-AI folder not found.", 404
    return send_from_directory(APP_WITH_AI_DIR, "index.html")


@app.route("/app/<path:filename>")
def app_with_ai_static(filename):
    """Serve static assets for Academic Arsenal with AI."""
    if not os.path.isdir(APP_WITH_AI_DIR):
        return "", 404
    return send_from_directory(APP_WITH_AI_DIR, filename)


@app.route("/api/music/list", methods=["GET", "OPTIONS"])
def music_list():
    """List audio files in the app's music folder for the player. Auto-updates music/playlist.json."""
    if request.method == "OPTIONS":
        return "", 204
    songs = []
    if os.path.isdir(MUSIC_DIR):
        for f in sorted(os.listdir(MUSIC_DIR)):
            if f.lower().endswith(ALLOWED_MUSIC_EXT):
                name = os.path.splitext(f)[0].replace("_", " ").replace("-", " ")
                songs.append({"file": f, "name": name})
        playlist_path = os.path.join(MUSIC_DIR, "playlist.json")
        try:
            with open(playlist_path, "w", encoding="utf-8") as out:
                json.dump({"songs": songs}, out, indent=2)
        except OSError:
            pass
    return jsonify({"songs": songs})


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


def _global_chat_rate_key():
    return request.remote_addr or "unknown"


@app.route("/api/global-chat/messages", methods=["GET", "OPTIONS"])
def global_chat_messages():
    if request.method == "OPTIONS":
        return "", 204
    since = request.args.get("since")
    try:
        since_ts = float(since) if since else 0
    except ValueError:
        since_ts = 0
    out = [m for m in GLOBAL_CHAT_MESSAGES if m.get("at_ts", 0) > since_ts]
    out.sort(key=lambda m: m.get("at_ts", 0))
    return jsonify({"messages": out[-100:]})  # last 100 after filter


@app.route("/api/global-chat/send", methods=["POST", "OPTIONS"])
def global_chat_send():
    if request.method == "OPTIONS":
        return "", 204
    data = request.get_json(silent=True) or {}
    display_name = (data.get("displayName") or "").strip()
    text = (data.get("text") or "").strip()
    user_id = (data.get("userId") or "").strip() or None
    if not display_name or len(display_name) > 64:
        return jsonify({"error": "displayName required (1–64 chars)"}), 400
    if not text or len(text) > 2000:
        return jsonify({"error": "text required (1–2000 chars)"}), 400
    rate_key = user_id or _global_chat_rate_key()
    now = time.time()
    if rate_key in _global_chat_last_send and (now - _global_chat_last_send[rate_key]) < GLOBAL_CHAT_RATE_LIMIT_SECONDS:
        return jsonify({"error": "Please wait a moment before sending again"}), 429
    _global_chat_last_send[rate_key] = now
    msg_id = str(uuid.uuid4())
    at_ts = time.time()
    at_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(at_ts))
    msg = {
        "id": msg_id,
        "userId": user_id,
        "displayName": display_name,
        "text": text,
        "at": at_iso,
        "at_ts": at_ts,
    }
    GLOBAL_CHAT_MESSAGES.append(msg)
    return jsonify({"id": msg_id, "at": at_iso, "at_ts": at_ts})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
