import os
from flask import Flask, render_template, request, send_file, jsonify
from moviepy.editor import VideoFileClip
from io import BytesIO
from PIL import Image
import mimetypes

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    videos = []
    for file in os.listdir(UPLOAD_FOLDER):
        if file.lower().endswith(('.mp4', '.mkv', '.mov', '.avi', '.webm')):
            path = os.path.join(UPLOAD_FOLDER, file)
            try:
                clip = VideoFileClip(path)
                duration = int(clip.duration)
                clip.close()
                videos.append({
                    "name": file,
                    "path": file,
                    "duration": f"{duration//60}:{duration%60:02d}"
                })
            except Exception:
                continue
    return render_template("index.html", videos=videos)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file", 400
    file = request.files["file"]
    if file.filename == "":
        return "No filename", 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return "Uploaded successfully"

@app.route("/thumbnail/<filename>")
def thumbnail(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return "Not Found", 404
    clip = VideoFileClip(path)
    frame = clip.get_frame(0.1)
    clip.close()
    img = Image.fromarray(frame)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return send_file(buf, mimetype="image/jpeg")

@app.route("/play/<filename>")
def play(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return "Not Found", 404
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "video/mp4"
    return send_file(path, mimetype=mime)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
