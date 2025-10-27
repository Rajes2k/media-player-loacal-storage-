import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED = {".mp4", ".mkv", ".webm", ".mov", ".ogg", ".mp3"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route("/")
def index():
    files = sorted(os.listdir(UPLOAD_FOLDER))
    videos = [f for f in files if os.path.splitext(f)[1].lower() in ALLOWED]
    return render_template("index.html", videos=videos)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f or f.filename == "":
        return redirect(url_for("index"))
    name = secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, name))
    return redirect(url_for("index"))

@app.route("/uploads/<path:filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, conditional=True)
